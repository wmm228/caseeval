#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量运行脚本 - 所有领域、所有模型、指定方法
遇到错误跳过继续执行

使用方法:
    python run_all.py --method simple
    python run_all.py --method simple 2>&1 | Tee-Object -FilePath output.log
"""

import os
import sys
import time
import argparse
import traceback
from datetime import datetime

# 设置stdout编码，解决Windows GBK问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from config import API_KEY, BASE_URL, GEN_MODELS, DOMAINS, EXAMPLE_FILES, EXAMPLE_TOPICS
from generator import CaseGenerator, load_example_case, load_topics, save_output


def run_all(method: str, examples_dir: str, data_dir: str, output_dir: str, 
            models: list = None, domains: list = None):
    """
    运行所有领域、所有模型的案例生成
    """
    # 默认所有模型和领域
    if models is None:
        models = list(GEN_MODELS.keys())
    if domains is None:
        domains = list(DOMAINS.keys())
    
    print("=" * 70)
    print(f"批量案例生成 - 全量运行")
    print("=" * 70)
    print(f"方法: {method}")
    print(f"模型: {models}")
    print(f"领域: {domains}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    sys.stdout.flush()
    
    # 统计
    total_stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped_models': [],
        'failed_cases': [],
        'total_input_tokens': 0,
        'total_output_tokens': 0,
    }
    
    # 遍历所有模型
    for model_key in models:
        model_name = MODELS[model_key]
        print(f"\n{'#' * 70}")
        print(f"# 模型: {model_key} ({model_name})")
        print(f"{'#' * 70}")
        sys.stdout.flush()
        
        # 初始化生成器
        try:
            generator = CaseGenerator(API_KEY, BASE_URL, model_name)
        except Exception as e:
            print(f"[错误] 初始化模型 {model_key} 失败: {e}")
            total_stats['skipped_models'].append(model_key)
            continue
        
        # 遍历所有领域
        for domain_key in domains:
            domain = DOMAINS[domain_key]
            print(f"\n{'=' * 60}")
            print(f"领域: {domain_key} ({domain})")
            print(f"{'=' * 60}")
            sys.stdout.flush()
            
            # 加载专家案例
            try:
                example_content = load_example_case(examples_dir, domain_key)
                example_domain = domain
                example_topic = EXAMPLE_TOPICS[domain_key]
            except Exception as e:
                print(f"[错误] 加载专家案例失败: {e}")
                traceback.print_exc()
                continue
            
            # 加载选题列表
            try:
                topics = load_topics(data_dir, domain_key)
            except Exception as e:
                print(f"[错误] 加载选题列表失败: {e}")
                traceback.print_exc()
                continue
            
            print(f"共 {len(topics)} 个选题")
            sys.stdout.flush()
            
            # 遍历所有选题
            for i, topic in enumerate(topics, 1):
                total_stats['total'] += 1
                print(f"\n[{i}/{len(topics)}] {topic}")
                sys.stdout.flush()
                
                try:
                    generator.reset_stats()
                    
                    # 根据方法生成
                    if method == 'simple':
                        result = generator.generate_simple(domain, topic)
                        save_output(output_dir, model_key, "simple", domain_key, topic, result)
                        
                    elif method == 'cot':
                        result = generator.generate_cot(domain, topic, example_domain, example_topic, example_content)
                        save_output(output_dir, model_key, "cot", domain_key, topic, result)
                        
                    elif method == 'gjmz':
                        outline, result = generator.generate_gjmz(domain, topic, example_domain, example_topic, example_content)
                        save_output(output_dir, model_key, "gjmz", domain_key, topic, outline, is_outline=True)
                        save_output(output_dir, model_key, "gjmz", domain_key, topic, result)
                    
                    # 统计token
                    stats = generator.token_stats.summary()
                    total_stats['total_input_tokens'] += stats.get('total_input_tokens', 0)
                    total_stats['total_output_tokens'] += stats.get('total_output_tokens', 0)
                    total_stats['success'] += 1
                    
                    print(f"  [OK] 成功 | Token: {stats.get('total_tokens', 0)}")
                    sys.stdout.flush()
                    
                except Exception as e:
                    total_stats['failed'] += 1
                    error_info = {
                        'model': model_key,
                        'domain': domain_key,
                        'topic': topic,
                        'error': str(e)
                    }
                    total_stats['failed_cases'].append(error_info)
                    print(f"  [FAIL] 失败: {e}")
                    traceback.print_exc()
                    sys.stdout.flush()
                    # 不中断，继续下一个
                
                # 避免请求过快
                time.sleep(1)
    
    # 打印总结
    print("\n" + "=" * 70)
    print("运行总结")
    print("=" * 70)
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总案例数: {total_stats['total']}")
    print(f"成功: {total_stats['success']}")
    print(f"失败: {total_stats['failed']}")
    print(f"跳过的模型: {total_stats['skipped_models']}")
    print(f"总Token: 输入={total_stats['total_input_tokens']} | 输出={total_stats['total_output_tokens']}")
    
    if total_stats['failed_cases']:
        print(f"\n失败案例列表:")
        for case in total_stats['failed_cases']:
            error_msg = str(case['error'])[:80]
            print(f"  - [{case['model']}] {case['domain']}/{case['topic']}: {error_msg}...")
    
    print("=" * 70)
    sys.stdout.flush()
    
    return total_stats


def main():
    parser = argparse.ArgumentParser(description='批量运行所有领域所有模型')
    parser.add_argument('--method', type=str, default='simple',
                        choices=['simple', 'cot', 'gjmz'],
                        help='生成方法')
    parser.add_argument('--models', type=str, nargs='+', default=None,
                        help='指定模型列表，如: --models qwen glm')
    parser.add_argument('--domains', type=str, nargs='+', default=None,
                        help='指定领域列表，如: --domains SE AI')
    parser.add_argument('--examples-dir', type=str, default='examples',
                        help='专家案例目录')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='数据目录')
    parser.add_argument('--output-dir', type=str, default='outputs',
                        help='输出目录')
    
    args = parser.parse_args()
    
    try:
        run_all(
            method=args.method,
            examples_dir=args.examples_dir,
            data_dir=args.data_dir,
            output_dir=args.output_dir,
            models=args.models,
            domains=args.domains
        )
    except KeyboardInterrupt:
        print("\n[中断] 用户取消运行")
    except Exception as e:
        print(f"\n[严重错误] {e}")
        traceback.print_exc()


if __name__ == '__main__':
    main()