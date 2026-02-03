#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Case Generator
Supports single test and batch generation

Usage:
    # Test single case
    python generator.py --domain SE --topic "Calendar Generator" --model qwen
    
    # Generate all cases for a domain
    python generator.py --domain SE --model qwen --all
    
    # List topics
    python generator.py --domain SE --list-topics
"""

import os
import sys
import argparse
import time
import json
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# Import config and prompt templates
from config import API_KEY, BASE_URL, GEN_MODELS, DOMAINS, EXAMPLE_FILES, EXAMPLE_TOPICS
from prompts import get_simple_prompt, get_cot_prompt, get_gjmz_stage1_prompt, get_gjmz_stage2_prompt


class TokenStats:
    """Token Statistics Class"""
    def __init__(self):
        self.records = []
    
    def add(self, method: str, stage: str, input_tokens: int, output_tokens: int):
        self.records.append({
            'method': method,
            'stage': stage,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens
        })
    
    def summary(self) -> dict:
        total_input = sum(r['input_tokens'] for r in self.records)
        total_output = sum(r['output_tokens'] for r in self.records)
        return {
            'total_input_tokens': total_input,
            'total_output_tokens': total_output,
            'total_tokens': total_input + total_output,
            'details': self.records
        }


class CaseGenerator:
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        self.token_stats = TokenStats()
        
    def call_api(self, prompt: str, method: str, stage: str = "main", max_retries: int = 3) -> str:
        """Call API to generate content"""
        for attempt in range(max_retries):
            try:
                print(f"  [API Call] {method}/{stage} Attempt {attempt + 1}...")
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=8000,
                )
                
                # Check for errors
                if hasattr(response, 'error') and response.error:
                    raise Exception(f"API returned error: {response.error}")
                
                # Check choices
                if not response.choices:
                    raise Exception("response.choices is empty")
                
                content = response.choices[0].message.content
                if content is None:
                    raise Exception("Response content is empty")
                
                # Count tokens
                input_tokens = response.usage.prompt_tokens if response.usage else 0
                output_tokens = response.usage.completion_tokens if response.usage else 0
                self.token_stats.add(method, stage, input_tokens, output_tokens)
                
                print(f"  [API Call] Success | Input:{input_tokens} Output:{output_tokens} | Content:{len(content)} chars")
                return content
                
            except Exception as e:
                print(f"  [API Call] Failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"  [API Call] Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    raise e
    
    def reset_stats(self):
        """Reset token statistics"""
        self.token_stats = TokenStats()
    
    def generate_simple(self, domain: str, topic: str) -> str:
        """Simple prompt generation (No expert example)"""
        print("\n[Simple Prompt] Start generating...")
        prompt = get_simple_prompt(domain=domain, topic=topic)
        result = self.call_api(prompt, "simple")
        print("[Simple Prompt] Generation completed")
        return result
    
    def generate_cot(self, domain: str, topic: str, example_domain: str,
                     example_topic: str, example_content: str) -> str:
        """Chain-of-Thought prompt generation"""
        print("\n[CoT Prompt] Start generating...")
        prompt = get_cot_prompt(domain, topic, example_domain, example_topic, example_content)
        result = self.call_api(prompt, "cot")
        print("[CoT Prompt] Generation completed")
        return result
    
    def generate_gjmz(self, domain: str, topic: str, example_domain: str,
                      example_topic: str, example_content: str) -> tuple:
        """Outline-Detail (GJMZ) generation (Two stages)"""
        print("\n[GJMZ Method] Start Stage 1: Generate Outline...")
        stage1_prompt = get_gjmz_stage1_prompt(domain, topic, example_domain, example_topic, example_content)
        outline = self.call_api(stage1_prompt, "gjmz", "stage1")
        print("[GJMZ Method] Stage 1 completed")
        
        print("[GJMZ Method] Start Stage 2: Generate Complete Case...")
        stage2_prompt = get_gjmz_stage2_prompt(domain, topic, example_domain, example_topic, example_content, outline)
        case_content = self.call_api(stage2_prompt, "gjmz", "stage2")
        print("[GJMZ Method] Stage 2 completed")
        
        return outline, case_content


def load_example_case(examples_dir: str, domain_key: str) -> str:
    """Load expert case for corresponding domain"""
    example_file = os.path.join(examples_dir, EXAMPLE_FILES[domain_key])
    with open(example_file, 'r', encoding='utf-8') as f:
        return f.read()


def load_topics(data_dir: str, domain_key: str) -> list:
    """Load all topics for a certain domain"""
    topic_file = os.path.join(data_dir, domain_key, f"{domain_key}.txt")
    with open(topic_file, 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip()]
    return topics


def save_output(output_dir: str, model: str, method: str, domain: str, 
                topic: str, content: str, is_outline: bool = False):
    """
    Save generation result
    Output structure: outputs/{model}/{method}/{domain}/{topic}.md
    """
    # Create output directory
    case_dir = os.path.join(output_dir, model, method, domain)
    os.makedirs(case_dir, exist_ok=True)
    
    # Filename
    safe_topic = topic.replace('/', '_').replace('\\', '_').replace(' ', '_').replace(':', '_')
    suffix = "_outline" if is_outline else ""
    filename = f"{safe_topic}{suffix}.md"
    filepath = os.path.join(case_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  [Save] {filepath}")
    return filepath


def generate_single_case(generator: CaseGenerator, domain_key: str, topic: str,
                         example_content: str, model_key: str, output_dir: str,
                         method: str = 'all') -> dict:
    """Generate single case with specified method"""
    domain = DOMAINS[domain_key]
    example_domain = DOMAINS[domain_key]
    example_topic = EXAMPLE_TOPICS[domain_key]
    
    results = {}
    generator.reset_stats()
    
    # Determine methods to run
    methods_to_run = ['simple', 'cot', 'gjmz'] if method == 'all' else [method]
    
    # 1. Simple Prompt
    if 'simple' in methods_to_run:
        try:
            start_time = time.time()
            simple_result = generator.generate_simple(domain, topic)
            simple_time = time.time() - start_time
            save_output(output_dir, model_key, "simple", domain_key, topic, simple_result)
            results['simple'] = {'success': True, 'time': simple_time, 'length': len(simple_result)}
        except Exception as e:
            print(f"[Simple Prompt] Failed: {e}")
            results['simple'] = {'success': False, 'error': str(e)}
    
    # 2. CoT Prompt
    if 'cot' in methods_to_run:
        try:
            start_time = time.time()
            cot_result = generator.generate_cot(domain, topic, example_domain, example_topic, example_content)
            cot_time = time.time() - start_time
            save_output(output_dir, model_key, "cot", domain_key, topic, cot_result)
            results['cot'] = {'success': True, 'time': cot_time, 'length': len(cot_result)}
        except Exception as e:
            print(f"[CoT Prompt] Failed: {e}")
            results['cot'] = {'success': False, 'error': str(e)}
    
    # 3. GJMZ Method
    if 'gjmz' in methods_to_run:
        try:
            start_time = time.time()
            outline, gjmz_result = generator.generate_gjmz(domain, topic, example_domain, example_topic, example_content)
            gjmz_time = time.time() - start_time
            save_output(output_dir, model_key, "gjmz", domain_key, topic, outline, is_outline=True)
            save_output(output_dir, model_key, "gjmz", domain_key, topic, gjmz_result)
            results['gjmz'] = {'success': True, 'time': gjmz_time, 'length': len(gjmz_result), 'outline_length': len(outline)}
        except Exception as e:
            print(f"[GJMZ Method] Failed: {e}")
            results['gjmz'] = {'success': False, 'error': str(e)}
    
    # Token Statistics
    results['token_stats'] = generator.token_stats.summary()
    
    return results


def run_single_test(domain_key: str, topic: str, model_key: str, 
                    examples_dir: str, data_dir: str, output_dir: str,
                    method: str = 'all'):
    """Run single test"""
    print("=" * 60)
    print(f"Case Generation Test")
    print("=" * 60)
    print(f"Domain: {domain_key} ({DOMAINS[domain_key]})")
    print(f"Topic: {topic}")
    print(f"Model: {model_key} ({GEN_MODELS[model_key]})")
    print(f"Method: {method}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load expert case
    print("\n[Prepare] Loading expert case...")
    example_content = load_example_case(examples_dir, domain_key)
    print(f"[Prepare] Expert case loaded, length: {len(example_content)} chars")
    
    # Initialize generator
    model_name = GEN_MODELS[model_key]
    print(f"\n[Prepare] Initializing API client ({model_name})...")
    generator = CaseGenerator(API_KEY, BASE_URL, model_name)
    
    # Generate case
    results = generate_single_case(generator, domain_key, topic, example_content, model_key, output_dir, method)
    
    # Print result summary
    print("\n" + "=" * 60)
    print("Generation Result Summary")
    print("=" * 60)
    for m in ['simple', 'cot', 'gjmz']:
        result = results.get(m, {})
        if not result:
            continue
        if result.get('success'):
            print(f"{m:10s}: Success | Time: {result['time']:.1f}s | Length: {result['length']} chars")
        else:
            print(f"{m:10s}: Failed | Error: {result.get('error', 'Unknown')}")
    
    # Token Statistics
    token_stats = results.get('token_stats', {})
    print("-" * 60)
    print(f"Token Stats: Input={token_stats.get('total_input_tokens', 0)} | "
          f"Output={token_stats.get('total_output_tokens', 0)} | "
          f"Total={token_stats.get('total_tokens', 0)}")
    print("=" * 60)
    
    return results


def run_batch_generation(domain_key: str, model_key: str,
                         examples_dir: str, data_dir: str, output_dir: str,
                         method: str = 'all'):
    """Batch generate all cases for a domain"""
    print("=" * 60)
    print(f"Batch Case Generation")
    print("=" * 60)
    print(f"Domain: {domain_key} ({DOMAINS[domain_key]})")
    print(f"Model: {model_key} ({GEN_MODELS[model_key]})")
    print(f"Method: {method}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load topics
    topics = load_topics(data_dir, domain_key)
    print(f"\n[Prepare] Total {len(topics)} topics to generate")
    
    # Load expert case
    print("[Prepare] Loading expert case...")
    example_content = load_example_case(examples_dir, domain_key)
    
    # Initialize generator
    model_name = GEN_MODELS[model_key]
    generator = CaseGenerator(API_KEY, BASE_URL, model_name)
    
    # Batch generation
    all_results = {}
    total_tokens = {'input': 0, 'output': 0}
    success_count = {'simple': 0, 'cot': 0, 'gjmz': 0}
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(topics)}] Generating: {topic}")
        print('='*60)
        
        try:
            results = generate_single_case(generator, domain_key, topic, example_content, model_key, output_dir, method)
            all_results[topic] = results
            
            # Statistics
            token_stats = results.get('token_stats', {})
            total_tokens['input'] += token_stats.get('total_input_tokens', 0)
            total_tokens['output'] += token_stats.get('total_output_tokens', 0)
            
            for m in ['simple', 'cot', 'gjmz']:
                if results.get(m, {}).get('success'):
                    success_count[m] += 1
                    
        except Exception as e:
            print(f"[Error] Generation Failed: {e}")
            all_results[topic] = {'error': str(e)}
        
        # Avoid rate limiting
        time.sleep(1)
    
    # Save summary result
    summary = {
        'domain': domain_key,
        'model': model_key,
        'total_topics': len(topics),
        'success_count': success_count,
        'total_tokens': total_tokens,
        'details': all_results
    }
    
    summary_path = os.path.join(output_dir, model_key, f"{domain_key}_summary.json")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Batch Generation Completed")
    print("=" * 60)
    print(f"Total Topics: {len(topics)}")
    print(f"Success Count: simple={success_count['simple']} | cot={success_count['cot']} | gjmz={success_count['gjmz']}")
    print(f"Total Tokens: Input={total_tokens['input']} | Output={total_tokens['output']} | Total={total_tokens['input']+total_tokens['output']}")
    print(f"Summary File: {summary_path}")
    print("=" * 60)
    
    return summary


def main():
    parser = argparse.ArgumentParser(description='Teaching Case Generator')
    parser.add_argument('--domain', type=str, default='SE', 
                        choices=list(DOMAINS.keys()),
                        help='Domain Code')
    parser.add_argument('--topic', type=str, default='Calendar Generator',
                        help='Case Topic')
    parser.add_argument('--model', type=str, default='qwen',
                        choices=list(GEN_MODELS.keys()),
                        help='Model Code')
    parser.add_argument('--examples-dir', type=str, default='examples',
                        help='Expert Examples Directory')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Data Directory')
    parser.add_argument('--output-dir', type=str, default='outputs',
                        help='Output Directory')
    parser.add_argument('--list-topics', action='store_true',
                        help='List all topics in specified domain')
    parser.add_argument('--all', action='store_true',
                        help='Generate all cases for specified domain')
    parser.add_argument('--method', type=str, default='all',
                        choices=['simple', 'cot', 'gjmz', 'all'],
                        help='Specify generation method (default all generates all three)')
    
    args = parser.parse_args()
    
    # List topics
    if args.list_topics:
        topics = load_topics(args.data_dir, args.domain)
        print(f"\nTopic List for {args.domain} ({DOMAINS[args.domain]}):")
        print("-" * 40)
        for i, topic in enumerate(topics, 1):
            print(f"{i:3d}. {topic}")
        print(f"\nTotal {len(topics)} topics")
        return
    
    # Batch generation
    if args.all:
        run_batch_generation(
            domain_key=args.domain,
            model_key=args.model,
            examples_dir=args.examples_dir,
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            method=args.method
        )
    else:
        # Single test
        run_single_test(
            domain_key=args.domain,
            topic=args.topic,
            model_key=args.model,
            examples_dir=args.examples_dir,
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            method=args.method
        )


if __name__ == '__main__':
    main()
