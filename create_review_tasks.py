#!/usr/bin/env python3
"""Create review tasks for completed implementation tasks"""

import json
from pathlib import Path
from datetime import datetime
import uuid

def create_review_tasks():
    """Create review tasks for completed implementation tasks"""
    try:
        # Load the coordinator state
        state_file = Path("mcp-coordinator/state.json")
        if not state_file.exists():
            print(f"Error: State file not found at {state_file}")
            return
            
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        # Find completed implementation tasks without review
        completed_impl = [t for t in state.get('task_queue', []) 
                         if t['type'] == 'implementation' and t['status'] == 'completed']
        
        # Check which ones already have review tasks
        existing_reviews = {t.get('context', {}).get('implementation_task_id') 
                           for t in state.get('task_queue', []) 
                           if t['type'] == 'review'}
        
        # Create review tasks for unreviewed implementations
        new_review_tasks = []
        for impl_task in completed_impl:
            if impl_task['id'] not in existing_reviews:
                review_task = {
                    'id': f"review-{str(uuid.uuid4())[:8]}",
                    'type': 'review',
                    'description': f"Review implementation: {impl_task['description']}",
                    'status': 'pending',
                    'priority': impl_task.get('priority', 'normal'),
                    'created_at': datetime.now().isoformat(),
                    'context': {
                        'implementation_task_id': impl_task['id'],
                        'implementation_details': impl_task.get('context', {}),
                        'result': impl_task.get('result', {})
                    }
                }
                new_review_tasks.append(review_task)
                print(f"✅ Created review task: {review_task['id']} for implementation {impl_task['id']}")
        
        if new_review_tasks:
            # Add new review tasks to the queue
            state['task_queue'].extend(new_review_tasks)
            
            # Save the updated state
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            print(f"\n📋 Created {len(new_review_tasks)} review tasks")
        else:
            print("No new review tasks needed - all implementations are already under review")
        
    except Exception as e:
        print(f"Error creating review tasks: {e}")

def main():
    print("Creating review tasks for completed implementations...")
    create_review_tasks()

if __name__ == "__main__":
    main()