#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案例生成器
支持单个测试和批量生成

使用方法:
    # 测试单个案例
    python generator.py --domain SE --topic "日历生成器" --model qwen
    
    # 生成一个领域的所有案例
    python generator.py --domain SE --model qwen --all
    
    # 列出选题
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

# 导入配置和提示模板
from config import API_KEY, BASE_URL, GEN_MODELS, DOMAINS, EXAMPLE_FILES, EXAMPLE_TOPICS
from prompts import get_simple_prompt, get_cot_prompt, get_gjmz_stage1_prompt, get_gjmz_stage2_prompt


class TokenStats:
    """Token统计类"""
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
        """调用API生成内容"""
        for attempt in range(max_retries):
            try:
                print(f"  [API调用] {method}/{stage} 第{attempt + 1}次尝试...")
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=8000,
                )
                
                # 检查错误
                if hasattr(response, 'error') and response.error:
                    raise Exception(f"API返回错误: {response.error}")
                
                # 检查choices
                if not response.choices:
                    raise Exception("response.choices 为空")
                
                content = response.choices[0].message.content
                if content is None:
                    raise Exception("响应内容为空")
                
                # 统计token
                input_tokens = response.usage.prompt_tokens if response.usage else 0
                output_tokens = response.usage.completion_tokens if response.usage else 0
                self.token_stats.add(method, stage, input_tokens, output_tokens)
                
                print(f"  [API调用] 成功 | 输入:{input_tokens} 输出:{output_tokens} | 内容:{len(content)}字符")
                return content
                
            except Exception as e:
                print(f"  [API调用] 失败: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"  [API调用] 等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise e
    
    def reset_stats(self):
        """重置token统计"""
        self.token_stats = TokenStats()
    
    def generate_simple(self, domain: str, topic: str) -> str:
        """简单提示生成（不使用专家案例）"""
        print("\n[简单提示] 开始生成...")
        prompt = get_simple_prompt(domain=domain, topic=topic)
        result = self.call_api(prompt, "simple")
        print("[简单提示] 生成完成")
        return result
    
    def generate_cot(self, domain: str, topic: str, example_domain: str,
                     example_topic: str, example_content: str) -> str:
        """思维链提示生成"""
        print("\n[思维链提示] 开始生成...")
        prompt = get_cot_prompt(domain, topic, example_domain, example_topic, example_content)
        result = self.call_api(prompt, "cot")
        print("[思维链提示] 生成完成")
        return result
    
    def generate_gjmz(self, domain: str, topic: str, example_domain: str,
                      example_topic: str, example_content: str) -> tuple:
        """纲举目张法生成（两阶段）"""
        print("\n[纲举目张法] 开始第一阶段：生成纲要...")
        stage1_prompt = get_gjmz_stage1_prompt(domain, topic, example_domain, example_topic, example_content)
        outline = self.call_api(stage1_prompt, "gjmz", "stage1")
        print("[纲举目张法] 第一阶段完成")
        
        print("[纲举目张法] 开始第二阶段：生成完整案例...")
        stage2_prompt = get_gjmz_stage2_prompt(domain, topic, example_domain, example_topic, example_content, outline)
        case_content = self.call_api(stage2_prompt, "gjmz", "stage2")
        print("[纲举目张法] 第二阶段完成")
        
        return outline, case_content


def load_example_case(examples_dir: str, domain_key: str) -> str:
    """加载对应领域的专家案例"""
    example_file = os.path.join(examples_dir, EXAMPLE_FILES[domain_key])
    with open(example_file, 'r', encoding='utf-8') as f:
        return f.read()


def load_topics(data_dir: str, domain_key: str) -> list:
    """加载某个领域的所有选题"""
    topic_file = os.path.join(data_dir, domain_key, f"{domain_key}.txt")
    with open(topic_file, 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip()]
    return topics


def save_output(output_dir: str, model: str, method: str, domain: str, 
                topic: str, content: str, is_outline: bool = False):
    """
    保存生成结果
    输出结构: outputs/{model}/{method}/{domain}/{topic}.md
    """
    # 创建输出目录
    case_dir = os.path.join(output_dir, model, method, domain)
    os.makedirs(case_dir, exist_ok=True)
    
    # 文件名
    safe_topic = topic.replace('/', '_').replace('\\', '_').replace(' ', '_').replace(':', '_')
    suffix = "_outline" if is_outline else ""
    filename = f"{safe_topic}{suffix}.md"
    filepath = os.path.join(case_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  [保存] {filepath}")
    return filepath


def generate_single_case(generator: CaseGenerator, domain_key: str, topic: str,
                         example_content: str, model_key: str, output_dir: str,
                         method: str = 'all') -> dict:
    """生成单个案例的指定方法"""
    domain = DOMAINS[domain_key]
    example_domain = DOMAINS[domain_key]
    example_topic = EXAMPLE_TOPICS[domain_key]
    
    results = {}
    generator.reset_stats()
    
    # 确定要运行的方法
    methods_to_run = ['simple', 'cot', 'gjmz'] if method == 'all' else [method]
    
    # 1. 简单提示
    if 'simple' in methods_to_run:
        try:
            start_time = time.time()
            simple_result = generator.generate_simple(domain, topic)
            simple_time = time.time() - start_time
            save_output(output_dir, model_key, "simple", domain_key, topic, simple_result)
            results['simple'] = {'success': True, 'time': simple_time, 'length': len(simple_result)}
        except Exception as e:
            print(f"[简单提示] 失败: {e}")
            results['simple'] = {'success': False, 'error': str(e)}
    
    # 2. 思维链提示
    if 'cot' in methods_to_run:
        try:
            start_time = time.time()
            cot_result = generator.generate_cot(domain, topic, example_domain, example_topic, example_content)
            cot_time = time.time() - start_time
            save_output(output_dir, model_key, "cot", domain_key, topic, cot_result)
            results['cot'] = {'success': True, 'time': cot_time, 'length': len(cot_result)}
        except Exception as e:
            print(f"[思维链提示] 失败: {e}")
            results['cot'] = {'success': False, 'error': str(e)}
    
    # 3. 纲举目张法
    if 'gjmz' in methods_to_run:
        try:
            start_time = time.time()
            outline, gjmz_result = generator.generate_gjmz(domain, topic, example_domain, example_topic, example_content)
            gjmz_time = time.time() - start_time
            save_output(output_dir, model_key, "gjmz", domain_key, topic, outline, is_outline=True)
            save_output(output_dir, model_key, "gjmz", domain_key, topic, gjmz_result)
            results['gjmz'] = {'success': True, 'time': gjmz_time, 'length': len(gjmz_result), 'outline_length': len(outline)}
        except Exception as e:
            print(f"[纲举目张法] 失败: {e}")
            results['gjmz'] = {'success': False, 'error': str(e)}
    
    # Token统计
    results['token_stats'] = generator.token_stats.summary()
    
    return results


def run_single_test(domain_key: str, topic: str, model_key: str, 
                    examples_dir: str, data_dir: str, output_dir: str,
                    method: str = 'all'):
    """运行单个测试"""
    print("=" * 60)
    print(f"案例生成测试")
    print("=" * 60)
    print(f"领域: {domain_key} ({DOMAINS[domain_key]})")
    print(f"选题: {topic}")
    print(f"模型: {model_key} ({GEN_MODELS[model_key]})")
    print(f"方法: {method}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 加载专家案例
    print("\n[准备] 加载专家案例...")
    example_content = load_example_case(examples_dir, domain_key)
    print(f"[准备] 专家案例加载完成，长度: {len(example_content)}字符")
    
    # 初始化生成器
    model_name = GEN_MODELS[model_key]
    print(f"\n[准备] 初始化API客户端 ({model_name})...")
    generator = CaseGenerator(API_KEY, BASE_URL, model_name)
    
    # 生成案例
    results = generate_single_case(generator, domain_key, topic, example_content, model_key, output_dir, method)
    
    # 打印结果汇总
    print("\n" + "=" * 60)
    print("生成结果汇总")
    print("=" * 60)
    for m in ['simple', 'cot', 'gjmz']:
        result = results.get(m, {})
        if not result:
            continue
        if result.get('success'):
            print(f"{m:10s}: 成功 | 耗时: {result['time']:.1f}秒 | 长度: {result['length']}字符")
        else:
            print(f"{m:10s}: 失败 | 错误: {result.get('error', 'Unknown')}")
    
    # Token统计
    token_stats = results.get('token_stats', {})
    print("-" * 60)
    print(f"Token统计: 输入={token_stats.get('total_input_tokens', 0)} | "
          f"输出={token_stats.get('total_output_tokens', 0)} | "
          f"总计={token_stats.get('total_tokens', 0)}")
    print("=" * 60)
    
    return results


def run_batch_generation(domain_key: str, model_key: str,
                         examples_dir: str, data_dir: str, output_dir: str,
                         method: str = 'all'):
    """批量生成一个领域的所有案例"""
    print("=" * 60)
    print(f"批量案例生成")
    print("=" * 60)
    print(f"领域: {domain_key} ({DOMAINS[domain_key]})")
    print(f"模型: {model_key} ({GEN_MODELS[model_key]})")
    print(f"方法: {method}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 加载选题列表
    topics = load_topics(data_dir, domain_key)
    print(f"\n[准备] 共 {len(topics)} 个选题待生成")
    
    # 加载专家案例
    print("[准备] 加载专家案例...")
    example_content = load_example_case(examples_dir, domain_key)
    
    # 初始化生成器
    model_name = GEN_MODELS[model_key]
    generator = CaseGenerator(API_KEY, BASE_URL, model_name)
    
    # 批量生成
    all_results = {}
    total_tokens = {'input': 0, 'output': 0}
    success_count = {'simple': 0, 'cot': 0, 'gjmz': 0}
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(topics)}] 生成: {topic}")
        print('='*60)
        
        try:
            results = generate_single_case(generator, domain_key, topic, example_content, model_key, output_dir, method)
            all_results[topic] = results
            
            # 统计
            token_stats = results.get('token_stats', {})
            total_tokens['input'] += token_stats.get('total_input_tokens', 0)
            total_tokens['output'] += token_stats.get('total_output_tokens', 0)
            
            for m in ['simple', 'cot', 'gjmz']:
                if results.get(m, {}).get('success'):
                    success_count[m] += 1
                    
        except Exception as e:
            print(f"[错误] 生成失败: {e}")
            all_results[topic] = {'error': str(e)}
        
        # 避免请求过快
        time.sleep(1)
    
    # 保存汇总结果
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
    
    # 打印总结
    print("\n" + "=" * 60)
    print("批量生成完成")
    print("=" * 60)
    print(f"总选题数: {len(topics)}")
    print(f"成功数量: simple={success_count['simple']} | cot={success_count['cot']} | gjmz={success_count['gjmz']}")
    print(f"Token总计: 输入={total_tokens['input']} | 输出={total_tokens['output']} | 总={total_tokens['input']+total_tokens['output']}")
    print(f"汇总文件: {summary_path}")
    print("=" * 60)
    
    return summary


def main():
    parser = argparse.ArgumentParser(description='教学案例生成器')
    parser.add_argument('--domain', type=str, default='SE', 
                        choices=list(DOMAINS.keys()),
                        help='领域代码')
    parser.add_argument('--topic', type=str, default='日历生成器',
                        help='案例选题')
    parser.add_argument('--model', type=str, default='qwen',
                        choices=list(GEN_MODELS.keys()),
                        help='模型代码')
    parser.add_argument('--examples-dir', type=str, default='examples',
                        help='专家案例目录')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='数据目录')
    parser.add_argument('--output-dir', type=str, default='outputs',
                        help='输出目录')
    parser.add_argument('--list-topics', action='store_true',
                        help='列出指定领域的所有选题')
    parser.add_argument('--all', action='store_true',
                        help='生成指定领域的所有案例')
    parser.add_argument('--method', type=str, default='all',
                        choices=['simple', 'cot', 'gjmz', 'all'],
                        help='指定生成方法（默认all生成全部三种）')
    
    args = parser.parse_args()
    
    # 列出选题
    if args.list_topics:
        topics = load_topics(args.data_dir, args.domain)
        print(f"\n{args.domain} ({DOMAINS[args.domain]}) 领域的选题列表:")
        print("-" * 40)
        for i, topic in enumerate(topics, 1):
            print(f"{i:3d}. {topic}")
        print(f"\n共 {len(topics)} 个选题")
        return
    
    # 批量生成
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
        # 单个测试
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