from re import T
from util.print_color import style,cprint
import operator
pass_list = []
fail_list = []
test_name = ''
test_name_title = f'{style.MAGENTA}TEST NAME: '

def assert_string_operator(inp, relate, cut):
    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '==': operator.eq,
            '!=': operator.ne} 
          
    assert ops[relate](inp, cut)

#DEPRECATED
def assertion_code_tester(expected_values,values,test_name,visible:bool=True):
    test_name = test_name.title()
    test_name_str = f'{test_name_title}{test_name}'

    try:
        assert expected_values == values
        print_str = f'{style.GREEN_BRIGHT}TEST PASSED - {expected_values} == {values} - {test_name_str}{style.RE}'
        pass_list.append(print_str)
        if visible:
            print(print_str)

    except AssertionError as e:
        print_str = f'{style.RED}TEST FAILED - {expected_values} != {values} - {test_name_str}{style.RE}'
        fail_list.append(print_str)
        if visible:
            print(print_str)
#DEPRECATED
def assertion_code_tester_not_equal(expected_values,values,test_name,visible:bool=True):
    test_name = test_name.title()
    test_name_str = f'{test_name_title}{test_name}'

    try:
        assert expected_values != values
        print_str = f'{style.GREEN_BRIGHT}TEST NOT EQUAL PASSED - {expected_values} != {values} - {test_name_str}{style.RE}'
        pass_list.append(print_str)
        if visible:
            print(print_str)

    except AssertionError as e:
        print_str = f'{style.RED}TEST NOT EQUAL FAILED - {expected_values} == {values} - {test_name_str}{style.RE}'
        fail_list.append(print_str)
        if visible:
            print(print_str)
#DEPRECATED
def assertion_code_tester_more_or_equal(expected_values,values,test_name,visible:bool=True):
    test_name = test_name.title()
    test_name_str = f'{test_name_title}{test_name}'

    try:
        assert expected_values >= values 
        print_str = f'{style.GREEN_BRIGHT}TEST MORE OR EQUAL PASSED - {expected_values} >= {values} - {test_name_str}{style.RE}'
        pass_list.append(print_str)
        if visible:
            print(print_str)

    except AssertionError as e:
        print_str = f'{style.RED}TEST MORE OR EQUAL FAILED - {expected_values} != {values} - {test_name_str}{style.RE}'
        fail_list.append(print_str)
        if visible:
            print(print_str)


def assert_code(expected_values:str,operator:str,values:str,test_name:str='',visible:bool=True):
    test_name = test_name.title()
    test_name_str = f'{test_name_title}{test_name}'
    try:
        # assert expected_values >= values 
        assert_string_operator(expected_values, operator, values)     
        print_str = f'{style.GREEN_BRIGHT}TEST PASSED - {expected_values} {operator} {values} - {test_name_str}{style.RE}'
        pass_list.append(print_str)
        if visible:
            print(print_str)

    except AssertionError as e:
        print_str = f'{style.RED}TEST FAILED - {expected_values} {operator} {values} - {test_name_str}{style.RE}'
        fail_list.append(print_str)
        if visible:
            print(print_str)

def display_total_tests(sum_only:bool=False):
    global pass_list
    global fail_list

    print(f'{style.YELLOW}TOTAL TESTS: {(len(pass_list) + len(fail_list))} {style.GREEN_BRIGHT} TESTS PASSED: {len(pass_list)} {style.WHITE} - {style.RED} TESTS FAILED: {len(fail_list)}',style.RE)
    if not sum_only:
        for print_item in pass_list:
            print(print_item)
        for print_item in fail_list:
            print(print_item)
        print(f'{style.YELLOW}TOTAL TESTS: {(len(pass_list) + len(fail_list))} {style.GREEN_BRIGHT} TESTS PASSED: {len(pass_list)} {style.WHITE} - {style.RED} TESTS FAILED: {len(fail_list)}',style.RE)
    pass_list = []
    fail_list = []


