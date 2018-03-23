from unittest.mock import patch
from monster_tracker.tracker import get_input

def test_no_args():
    user_input = 'asdf'
    with patch('builtins.input', side_effect=[user_input]):
        data = get_input()
    assert data == user_input

def test_query_string():
    user_input = 'asdf'
    with patch('builtins.input', side_effect=[user_input]) as mock:
        data = get_input('Enter a string')
    assert data == user_input

def test_invalid_query():
    user_input = 'asdf'
    with patch('builtins.input', side_effect=[user_input]):
        data = get_input(1)

def test_correct_type():
    user_input = ['asdf', '1']
    with patch('builtins.input', side_effect=user_input):
        data = get_input(query_string='Enter a number', out_type=int)
    assert data == 1

def test_passes_condition():
    user_input = ['asdf', '1']
    with patch('builtins.input', side_effect=user_input):
        data = get_input(conditions=(lambda x: x.isdecimal(), 'Input is not a decimal number'))
    assert data == '1'

def test_input_and_condition():
    user_input = ['1234', '9001']
    with patch('builtins.input', side_effect=user_input):
        data = get_input(out_type=int, conditions=(lambda x: x > 9000, 'Input is not over 9000'))
    assert data == 9001


def test_query_is_fstring():
    user_input = 'asdf'
    with patch('builtins.input', side_effect=[user_input]):
        data = get_input(query_string=f'Enter {user_input}')
    assert data==user_input

def test_choices():
    user_input = '1'
    with patch('builtins.input', side_effect=[user_input]):
        data = get_input(choices=[2, 3, 4, 5, 6])
    assert data == '2'

