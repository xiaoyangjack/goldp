#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取新闻数据的Python脚本
用于后端API调用
"""
import sys
import json
from news_fetcher import get_sentiment_stats, fetch_news

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print(json.dumps({
            'code': 400,
            'message': 'Invalid arguments'
        }))
        return
    
    command = sys.argv[1]
    
    try:
        if command == 'sentiment':
            stats = get_sentiment_stats()
            print(json.dumps({
                'code': 200,
                'data': stats,
                'message': 'success'
            }))
        elif command == 'list':
            news_df = fetch_news()
            news_list = news_df.to_dict('records')
            print(json.dumps({
                'code': 200,
                'data': news_list,
                'message': 'success'
            }))
        else:
            print(json.dumps({
                'code': 400,
                'message': 'Invalid command'
            }))
    except Exception as e:
        print(json.dumps({
            'code': 500,
            'message': str(e)
        }))

if __name__ == "__main__":
    main()
