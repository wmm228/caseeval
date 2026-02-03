#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Evaluation Script

Output Structure:
{output_root}/{model}/{method}/{domain}/{eval_model}.jsonl
Each line is a JSON object of a case's evaluation result (containing meta-info and 6 scores).
"""

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Set, Tuple

from config import API_KEY, BASE_URL, DOMAINS, EVAL_MODELS
from prompts import get_eval_prompt


EXPECTED_SCORE_KEYS = (
    "structure_consistency",
    "topic_relevance",
    "content_clarity",
    "concept_completeness",
    "theory_correctness",
    "design_feasibility",
)


@dataclass(frozen=True)
class CaseItem:
    model: str
    method: str
    domain: str
    topic: str
    md_path: Path


def iter_case_items(input_root: Path, model: str, method: str, domain: str) -> Iterable[CaseItem]:
    base_dir = input_root / model / method / domain
    if not base_dir.exists():
        return

    for p in sorted(base_dir.glob("*.md")):
        if p.name.endswith("_outline.md"):
            continue
        yield CaseItem(
            model=model,
            method=method,
            domain=domain,
            topic=p.stem,
            md_path=p,
        )


def read_existing_topics(jsonl_path: Path) -> Set[str]:
    if not jsonl_path.exists():
        return set()

    topics: Set[str] = set()
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            topic = obj.get("topic")
            if isinstance(topic, str) and topic:
                topics.add(topic)
    return topics


def extract_first_json_object(text: str) -> Optional[str]:
    s = text.strip()
    if not s:
        return None

    start = s.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_string:
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            depth += 1
            continue
        if ch == "}":
            depth -= 1
            if depth == 0:
                return s[start : i + 1]
            continue
    return None


def extract_scores_from_text(text: str) -> Optional[Dict[str, int]]:
    cn_map = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5}
    labels: Dict[str, Tuple[str, ...]] = {
        "structure_consistency": ("structure_consistency", "Structure Consistency", "结构一致性"),
        "topic_relevance": ("topic_relevance", "Topic Relevance", "主题相关性"),
        "content_clarity": ("content_clarity", "Content Clarity", "内容清晰性"),
        "concept_completeness": ("concept_completeness", "Concept Completeness", "概念完备性"),
        "theory_correctness": ("theory_correctness", "Theory Correctness", "理论准确性"),
        "design_feasibility": ("design_feasibility", "Design Feasibility", "设计可行性"),
    }

    found: Dict[str, int] = {}
    for k, ks in labels.items():
        for label in ks:
            m = re.search(rf"{re.escape(label)}\s*[:：]\s*([1-5一二三四五])", text, flags=re.IGNORECASE)
            if m:
                token = m.group(1)
                found[k] = int(token) if token.isdigit() else cn_map[token]
                break

    if len(found) == len(EXPECTED_SCORE_KEYS):
        return found

    digits = re.findall(r"(?<!\d)([1-5])(?!\d)", text)
    if len(digits) < len(EXPECTED_SCORE_KEYS):
        cn_digits = re.findall(r"([一二三四五])", text)
        if len(cn_digits) < len(EXPECTED_SCORE_KEYS):
            return None
        return {k: cn_map[cn_digits[i]] for i, k in enumerate(EXPECTED_SCORE_KEYS)}

    return {k: int(digits[i]) for i, k in enumerate(EXPECTED_SCORE_KEYS)}


def normalize_scores(obj: Dict[str, Any]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for k in EXPECTED_SCORE_KEYS:
        if k not in obj:
            raise ValueError(f"missing key: {k}")
        v = obj[k]
        if isinstance(v, bool):
            raise ValueError(f"invalid score for {k}: {v}")
        if isinstance(v, (int, float)):
            vv = int(v)
        elif isinstance(v, str):
            vv = int(v.strip())
        else:
            raise ValueError(f"invalid score type for {k}: {type(v)}")
        if vv < 1 or vv > 5:
            raise ValueError(f"score out of range for {k}: {vv}")
        result[k] = vv
    return result


def create_openai_client() -> Any:
    try:
        from openai import OpenAI
    except Exception as e:
        raise RuntimeError("missing dependency: openai") from e
    return OpenAI(api_key=API_KEY, base_url=BASE_URL)


def call_eval_api(
    client: Any,
    model_name: str,
    prompt: str,
    max_retries: int,
    sleep_seconds: float,
    max_tokens: int,
) -> Dict[str, int]:
    def get_message_text(message: Any) -> str:
        content = getattr(message, "content", None)
        if isinstance(content, str) and content.strip():
            return content
        reasoning = getattr(message, "reasoning_content", None)
        if isinstance(reasoning, str) and reasoning.strip():
            return reasoning
        return ""

    last_err: Optional[Exception] = None
    for attempt in range(max_retries):
        try:
            print(f"  Attempt {attempt+1}/{max_retries} calling {model_name}...")
            request_model = model_name
            # For Gemini 3, increase tokens to avoid truncation during reasoning
            # User confirmed to increase token
            current_max_tokens = max_tokens
            if "gemini-3" in request_model:
                current_max_tokens = max(current_max_tokens, 8192)

            request_kwargs: Dict[str, Any] = dict(
                model=request_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=current_max_tokens,
            )

            try:
                response = client.chat.completions.create(**request_kwargs)
            except Exception:
                # Fallback without json_object if it failed
                response = client.chat.completions.create(**request_kwargs)

            if not response.choices:
                print(f"  Attempt {attempt+1} failed: response.choices is empty")
                try:
                    print(f"  DEBUG response: {response}")
                except Exception as e:
                    print(f"  DEBUG response print failed: {e}")
                raise RuntimeError("response.choices is empty")
            
            # Debug print for full response info
            choice = response.choices[0]
            print(f"  Attempt {attempt+1} finish_reason: {getattr(choice, 'finish_reason', 'unknown')}")
            
            message = choice.message
            content = get_message_text(message)
            
            # Print raw message attributes for debugging
            # print(f"  Debug: content={repr(getattr(message, 'content', None))}, reasoning={repr(getattr(message, 'reasoning_content', None))}")

            # If content is empty and it was Gemini 3, maybe try WITH json_object?
            # Or maybe it was filtered?
            if not content.strip() and "gemini-3" in request_model:
                # Retry with json_object just in case? Or just retry?
                # Actually, user said "instruction following problem".
                # Maybe we should try to add "JSON" to the prompt start?
                # But prompt already has "Output only JSON".
                pass
            
            if not content.strip():
                print(f"  Attempt {attempt+1} failed: empty response content")
                raise RuntimeError("empty response content")
            
            print(f"  Attempt {attempt+1} response content: {content[:1000]}") # Print first 1000 chars

            try:
                raw_obj = json.loads(content)
            except Exception:
                # Try to extract from markdown code block first
                code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
                if code_block_match:
                    try:
                        raw_obj = json.loads(code_block_match.group(1))
                    except Exception:
                        raw_obj = None
                else:
                    raw_obj = None

                if raw_obj is None:
                    extracted = extract_first_json_object(content)
                    if extracted:
                        try:
                            raw_obj = json.loads(extracted)
                        except Exception:
                            # If first { ... } is not valid JSON (e.g. part of reasoning), try to find subsequent ones?
                            # For now, fall back to text extraction
                            pass

                if raw_obj is None:
                    extracted_scores = extract_scores_from_text(content)
                    if extracted_scores is None:
                        snippet = content.strip().replace("\r", " ").replace("\n", " ")
                        raise RuntimeError(f"failed to parse json from response (len={len(content)}): {snippet[:500]}")
                    raw_obj = extracted_scores

            if not isinstance(raw_obj, dict):
                raise RuntimeError("response json is not an object")
            return normalize_scores(raw_obj)
        except Exception as e:
            print(f"  Attempt {attempt+1} exception: {e}")
            last_err = e
            if attempt < max_retries - 1:
                print(f"  Sleeping {sleep_seconds}s before retry...")
                time.sleep((attempt + 1) * sleep_seconds)
            else:
                break
    raise RuntimeError(f"eval api failed: {last_err}")


def ensure_parent_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def write_jsonl_line(path: Path, obj: Dict[str, Any]) -> None:
    ensure_parent_dir(path)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def build_output_path(output_root: Path, model: str, method: str, domain: str, eval_model_label: str) -> Path:
    return output_root / model / method / domain / f"{eval_model_label}.jsonl"


def evaluate_cases(
    input_root: Path,
    output_root: Path,
    model: str,
    method: str,
    domain: str,
    eval_model_key: str,
    eval_model_label: str,
    max_cases: Optional[int],
    dry_run: bool,
    resume: bool,
    max_retries: int,
    sleep_seconds: float,
    max_tokens: int,
) -> Tuple[int, int]:
    eval_model_name = EVAL_MODELS.get(eval_model_key, eval_model_key)
    client = None if dry_run else create_openai_client()

    out_path = build_output_path(output_root, model, method, domain, eval_model_label)
    existing_topics = read_existing_topics(out_path) if resume else set()

    processed = 0
    skipped = 0
    for item in iter_case_items(input_root, model, method, domain):
        if item.topic in existing_topics:
            skipped += 1
            continue
        if max_cases is not None and processed >= max_cases:
            break

        if dry_run:
            processed += 1
            continue

        case_text = item.md_path.read_text(encoding="utf-8", errors="replace")
        domain_display = DOMAINS.get(domain, domain)
        prompt = get_eval_prompt(domain=domain_display, topic=item.topic, case_content=case_text)
        if eval_model_name == "gemini-3-pro-preview":
            # For Gemini 3, try to append prompt instruction to ensure JSON
            prompt += "\n\nImportant: The model is allowed to reason, but the FINAL output MUST be a valid JSON object."
            pass

        print(f"[{time.strftime('%H:%M:%S')}] processing: {item.topic} (model={model}, method={method}, domain={domain})")
        scores = call_eval_api(
            client=client,
            model_name=eval_model_name,
            prompt=prompt,
            max_retries=max_retries,
            sleep_seconds=sleep_seconds,
            max_tokens=max_tokens,
        )
        record: Dict[str, Any] = {
            "model": item.model,
            "method": item.method,
            "domain": item.domain,
            "topic": item.topic,
            "eval_model": eval_model_label,
        }
        record.update(scores)
        write_jsonl_line(out_path, record)
        processed += 1
        time.sleep(sleep_seconds)

    return processed, skipped


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automatic Teaching Case Evaluation Script (Output jsonl)")
    parser.add_argument("--input-root", type=str, default="outputs", help="Generated cases root directory")
    parser.add_argument("--output-root", type=str, default="auto_eval", help="Evaluation results root directory")

    parser.add_argument("--model", type=str, required=True, help="Generated model code to be evaluated (e.g. doubao)")
    parser.add_argument("--method", type=str, required=True, choices=["simple", "cot", "gjmz"], help="Generation method")
    parser.add_argument("--domain", type=str, required=True, choices=list(DOMAINS.keys()), help="Domain code")

    parser.add_argument("--eval-model", type=str, required=True, help="Evaluation model code or name")
    parser.add_argument("--eval-model-label", type=str, default="", help="Evaluation model label (written to jsonl and filename)")

    parser.add_argument("--max-cases", type=int, default=None, help="Maximum number of cases to evaluate")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, do not call model, do not write files")
    parser.add_argument("--no-resume", action="store_true", help="Do not read existing jsonl, do not skip evaluated topics")

    parser.add_argument("--max-retries", type=int, default=3, help="Number of retries on failure")
    parser.add_argument("--sleep", type=float, default=1.0, help="Call interval seconds (including retry backoff base)")
    parser.add_argument("--max-tokens", type=int, default=300, help="Max tokens for evaluation output")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_root = Path(args.input_root)
    output_root = Path(args.output_root)

    eval_model_key = args.eval_model
    eval_model_label = args.eval_model_label.strip() or f"eval-{eval_model_key}"

    processed, skipped = evaluate_cases(
        input_root=input_root,
        output_root=output_root,
        model=args.model,
        method=args.method,
        domain=args.domain,
        eval_model_key=eval_model_key,
        eval_model_label=eval_model_label,
        max_cases=args.max_cases,
        dry_run=args.dry_run,
        resume=not args.no_resume,
        max_retries=args.max_retries,
        sleep_seconds=args.sleep,
        max_tokens=args.max_tokens,
    )

    out_path = build_output_path(output_root, args.model, args.method, args.domain, eval_model_label)
    print("=" * 60)
    print("Automatic Evaluation Completed")
    print("=" * 60)
    print(f"Input Directory: {input_root}")
    print(f"Output File: {out_path}")
    print(f"Eval Model: {eval_model_key} -> {EVAL_MODELS.get(eval_model_key, eval_model_key)}")
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    print("=" * 60)


if __name__ == "__main__":
    if os.name == "nt":
        try:
            import sys

            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    main()
