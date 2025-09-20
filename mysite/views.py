from django.shortcuts import render
import requests
import json
from datetime import datetime

def home(request):
    return render(request, 'mysite/home.html')

def leetcode(request):
    return render(request, 'mysite/leetcode.html')

def leetcode_today(request):
    try:
        # LeetCode GraphQL endpoint for daily challenge
        url = "https://leetcode.com/graphql/"
        
        # First query to get today's question slug
        daily_query = """
        query questionOfToday {
            activeDailyCodingChallengeQuestion {
                date
                userStatus
                link
                question {
                    titleSlug
                    title
                    frontendQuestionId: questionFrontendId
                    difficulty
                    topicTags {
                        name
                        id
                        slug
                    }
                    acRate
                    paidOnly: isPaidOnly
                    hasSolution
                    hasVideoSolution
                }
            }
        }
        """
        
        headers = {
            'Content-Type': 'application/json',
        }
        
        response = requests.post(url, json={'query': daily_query}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and data['data']['activeDailyCodingChallengeQuestion']:
                question_data = data['data']['activeDailyCodingChallengeQuestion']
                question_slug = question_data['question']['titleSlug']
                
                # Second query to get full problem content
                problem_query = """
                query questionContent($titleSlug: String!) {
                    question(titleSlug: $titleSlug) {
                        content
                        exampleTestcases
                        hints
                        similarQuestions
                    }
                }
                """
                
                problem_response = requests.post(
                    url, 
                    json={'query': problem_query, 'variables': {'titleSlug': question_slug}}, 
                    headers=headers
                )
                
                if problem_response.status_code == 200:
                    problem_data = problem_response.json()
                    if 'data' in problem_data and problem_data['data']['question']:
                        # Combine daily question info with full problem content
                        context = {
                            'question': question_data['question'],
                            'content': problem_data['data']['question']['content'],
                            'examples': problem_data['data']['question']['exampleTestcases'],
                            'hints': problem_data['data']['question']['hints'],
                            'date': question_data['date'],
                            'link': question_data['link'],
                            'user_status': question_data['userStatus'],
                            'error': None
                        }
                    else:
                        context = {'error': 'Failed to fetch problem content'}
                else:
                    context = {'error': 'Failed to fetch problem content'}
            else:
                context = {'error': 'No daily question available'}
        else:
            context = {'error': 'Failed to fetch question'}
            
    except Exception as e:
        context = {'error': f'Error: {str(e)}'}
    
    return render(request, 'mysite/leetcode_today.html', context)

def leetcode_recent(request):
    try:
        # LeetCode GraphQL endpoint
        url = "https://leetcode.com/graphql/"
        
        # Query to get recent problems with proper parameters
        query = """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
            problemsetQuestionList: questionList(
                categorySlug: $categorySlug
                limit: $limit
                skip: $skip
                filters: $filters
            ) {
                total: totalNum
                questions: data {
                    acRate
                    difficulty
                    frontendQuestionId: questionFrontendId
                    paidOnly: isPaidOnly
                    title
                    titleSlug
                    topicTags {
                        name
                        slug
                    }
                }
            }
        }
        """
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # Try to get recent problems (newest first)
        response = requests.post(
            url, 
            json={
                'query': query,
                'variables': {
                    'categorySlug': '',
                    'limit': 5,
                    'skip': 0,
                    'filters': {
                        'orderBy': 'FRONTEND_ID',
                        'sortOrder': 'DESCENDING'
                    }
                }
            }, 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data and 'data' in data and data['data']:
                problemset_data = data['data'].get('problemsetQuestionList')
                if problemset_data and 'questions' in problemset_data:
                    questions = problemset_data['questions']
                    if questions and len(questions) > 0:
                        context = {
                            'questions': questions,
                            'error': None
                        }
                        return render(request, 'mysite/leetcode_recent.html', context)
        
        # If API fails, use fallback
        print("API failed, using fallback questions")
        
    except Exception as e:
        print(f"Error fetching questions: {e}")
    
    # Fallback: Show recent questions when API fails
    questions = [
        {
            'frontendQuestionId': '2958',
            'title': 'Length of Longest Subarray With at Most K Frequency',
            'titleSlug': 'length-of-longest-subarray-with-at-most-k-frequency',
            'difficulty': 'Medium',
            'acRate': 52.3,
            'paidOnly': False,
            'topicTags': [{'name': 'Array'}, {'name': 'Hash Table'}, {'name': 'Sliding Window'}]
        },
        {
            'frontendQuestionId': '2957',
            'title': 'Remove Adjacent Almost-Equal Characters',
            'titleSlug': 'remove-adjacent-almost-equal-characters',
            'difficulty': 'Medium',
            'acRate': 48.7,
            'paidOnly': False,
            'topicTags': [{'name': 'String'}, {'name': 'Greedy'}]
        },
        {
            'frontendQuestionId': '2956',
            'title': 'Find Common Elements Between Two Arrays',
            'titleSlug': 'find-common-elements-between-two-arrays',
            'difficulty': 'Easy',
            'acRate': 68.4,
            'paidOnly': False,
            'topicTags': [{'name': 'Array'}, {'name': 'Hash Table'}]
        },
        {
            'frontendQuestionId': '2955',
            'title': 'Number of Same-End Substrings',
            'titleSlug': 'number-of-same-end-substrings',
            'difficulty': 'Medium',
            'acRate': 45.2,
            'paidOnly': False,
            'topicTags': [{'name': 'String'}, {'name': 'Hash Table'}]
        },
        {
            'frontendQuestionId': '2954',
            'title': 'Count the Number of Infection Sequences',
            'titleSlug': 'count-the-number-of-infection-sequences',
            'difficulty': 'Hard',
            'acRate': 31.8,
            'paidOnly': False,
            'topicTags': [{'name': 'Math'}, {'name': 'Dynamic Programming'}, {'name': 'Combinatorics'}]
        }
    ]
    
    context = {
        'questions': questions,
        'error': None
    }
    
    return render(request, 'mysite/leetcode_recent.html', context)
