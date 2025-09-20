from django.shortcuts import render
import requests
import json
from datetime import datetime

def home(request):
    return render(request, 'mysite/home.html')

def leetcode(request):
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
    
    return render(request, 'mysite/leetcode.html', context)
