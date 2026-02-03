#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Run Script - All domains, all models, specified method
Skip and continue on error

Usage:
    python run_all.py --method simple
    python run_all.py --method simple 2>&1 | Tee-Object -FilePath output.log
"""

import os
import sys
import time
import argparse
import traceback
from datetime import datetime

# Set stdout encoding to solve Windows GBK issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from config import API_KEY, BASE_URL, GEN_MODELS, DOMAINS, EXAMPLE_FILES, EXAMPLE_TOPICS
from generator import CaseGenerator, load_example_case, load_topics, save_output


def run_all(method: str, examples_dir: str, data_dir: str, output_dir: str, 
            models: list = None, domains: list = None):
    """
    Run case generation for all domains and all models
    """
    # Default to all models and domains
    if models is None:
        models = list(GEN_MODELS.keys())
    if domains is None:
        domains = list(DOMAINS.keys())
    
    print("=" * 70)
    print(f"Batch Case Generation - Full Run")
    print("=" * 70)
    print(f"Method: {method}")
    print(f"Models: {models}")
    print(f"Domains: {domains}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    sys.stdout.flush()
    
    # Statistics
    total_stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped_models': [],
        'failed_cases': [],
        'total_input_tokens': 0,
        'total_output_tokens': 0,
    }
    
    # Iterate over all models
    for model_key in models:
        model_name = GEN_MODELS[model_key]
        print(f"\n{'#' * 70}")
        print(f"# Model: {model_key} ({model_name})")
        print(f"{'#' * 70}")
        sys.stdout.flush()
        
        # Initialize generator
        try:
            generator = CaseGenerator(API_KEY, BASE_URL, model_name)
        except Exception as e:
            print(f"[Error] Failed to initialize model {model_key}: {e}")
            total_stats['skipped_models'].append(model_key)
            continue
        
        # Iterate over all domains
        for domain_key in domains:
            domain = DOMAINS[domain_key]
            print(f"\n{'=' * 60}")
            print(f"Domain: {domain_key} ({domain})")
            print(f"{'=' * 60}")
            sys.stdout.flush()
            
            # Load expert case
            try:
                example_content = load_example_case(examples_dir, domain_key)
                example_domain = domain
                example_topic = EXAMPLE_TOPICS[domain_key]
            except Exception as e:
                print(f"[Error] Failed to load expert case: {e}")
                traceback.print_exc()
                continue
            
            # Load topic list
            try:
                topics = load_topics(data_dir, domain_key)
            except Exception as e:
                print(f"[Error] Failed to load topic list: {e}")
                traceback.print_exc()
                continue
            
            print(f"Total {len(topics)} topics")
            sys.stdout.flush()
            
            # Iterate over all topics
            for i, topic in enumerate(topics, 1):
                total_stats['total'] += 1
                print(f"\n[{i}/{len(topics)}] {topic}")
                sys.stdout.flush()
                
                try:
                    generator.reset_stats()
                    
                    # Generate based on method
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
                    
                    # Count tokens
                    stats = generator.token_stats.summary()
                    total_stats['total_input_tokens'] += stats.get('total_input_tokens', 0)
                    total_stats['total_output_tokens'] += stats.get('total_output_tokens', 0)
                    total_stats['success'] += 1
                    
                    print(f"  [OK] Success | Token: {stats.get('total_tokens', 0)}")
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
                    print(f"  [FAIL] Failed: {e}")
                    traceback.print_exc()
                    sys.stdout.flush()
                    # Do not interrupt, continue to next
                
                # Avoid rate limiting
                time.sleep(1)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Run Summary")
    print("=" * 70)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Cases: {total_stats['total']}")
    print(f"Success: {total_stats['success']}")
    print(f"Failed: {total_stats['failed']}")
    print(f"Skipped Models: {total_stats['skipped_models']}")
    print(f"Total Tokens: Input={total_stats['total_input_tokens']} | Output={total_stats['total_output_tokens']}")
    
    if total_stats['failed_cases']:
        print(f"\nFailed Case List:")
        for case in total_stats['failed_cases']:
            error_msg = str(case['error'])[:80]
            print(f"  - [{case['model']}] {case['domain']}/{case['topic']}: {error_msg}...")
    
    print("=" * 70)
    sys.stdout.flush()
    
    return total_stats


def main():
    parser = argparse.ArgumentParser(description='Batch run all domains all models')
    parser.add_argument('--method', type=str, default='simple',
                        choices=['simple', 'cot', 'gjmz'],
                        help='Generation method')
    parser.add_argument('--models', type=str, nargs='+', default=None,
                        help='Specify model list, e.g.: --models qwen glm')
    parser.add_argument('--domains', type=str, nargs='+', default=None,
                        help='Specify domain list, e.g.: --domains SE AI')
    parser.add_argument('--examples-dir', type=str, default='examples',
                        help='Expert Examples Directory')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Data Directory')
    parser.add_argument('--output-dir', type=str, default='outputs',
                        help='Output Directory')
    
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
        print("\n[Interrupt] User cancelled run")
    except Exception as e:
        print(f"\n[Critical Error] {e}")
        traceback.print_exc()


if __name__ == '__main__':
    main()
