# -------------------------------------------
#    ALGORITHMS AND DATA STRUCTURES
#    Final Project
#    February, 2023
# -------------------------------------------


from random import seed, randint
from time import time


# -------------------------------------------
#    Solution
# -------------------------------------------


def merge(a: list, b: list) -> list:
    """Merge two sorted lists into a single sorted list.

    Args:
        a (list): First sorted list.
        b (list): Second sorted list.

    Returns:
        list: A single sorted list with elements from both a and b.

    """
    c = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            c.append(a[i])
            i += 1
        else:
            c.append(b[j])
            j += 1
    c.extend(a[i:])
    c.extend(b[j:])
    return c


def find_percentile(a: list, b: list, p: int) -> int:
    """Find the p-th percentile of the merged list.

    Args:
        a (list): First sorted list.
        b (list): Second sorted list.
        p (int): The p-th percentile to be calculated.

    Returns:
        int: The p-th percentile of the merged list.

    """
    c = merge(a, b)
    k = int(-(-p*len(c) // 100)) - 1
    return c[k]


# -------------------------------------------
#    Major test function
# -------------------------------------------


def test_find_percentile(a: list, b: list, p: int, correct_answer: int) -> None:
    """Test the find_percentile function.

    Args:
        a (list): First sorted list.
        b (list): Second sorted list.
        p (int): The p-th percentile to be calculated.
        correct_answer (int): The correct answer for the test.

    """
    percentile = find_percentile(a, b, p)
    error_str = '>>> Test FAILED:\nInput: {0}\nOutput: {1}\nCorrect output: {2}'
    assert percentile == correct_answer, error_str.format((a, b, p), percentile, correct_answer)


# -------------------------------------------
#     Auxiliary, supportive functions
# -------------------------------------------


def get_random_test(test_size: int, right_border: int) -> list:
    """Generate a random list with a given size and maximum value.

    Args:
        test_size (int): The size of the random list.
        right_border (int): The maximum value for the elements in the list.

    Returns:
        list: A random list with elements between 0 and right_border.

    """
    test = []
    for i in range(test_size):
        test.append(randint(0, right_border))
    test.sort()
    return test


def binary_search(c: list, k: int) -> int:
    """Perform a binary search to find the k-th element in a sorted list.

    Args:
        c (list): A sorted list.
        k (int): The index of the element to be found.

    Returns:
        int: The k-th element in the sorted list.

    """
    low = 0
    high = len(c)-1
    while low <= high:
        mid = (low + high) // 2
        count = sum(x <= c[mid] for x in c[:mid+1])
        if count == k:
            return c[mid]
        elif count < k:
            low = mid + 1
        else:
            high = mid - 1
    return c[low]


def reference_solution(a, b, p):
    """
    Returns the p-th percentile of the concatenation of two sorted lists a and b.

    Args:
        a (list): First sorted list.
        b (list): Second sorted list.
        p (int): The percentile to find.

    Returns:
        int: The p-th percentile.

    """
    c = a + b  # concatenate the two lists
    c.sort()  # sort the concatenated list
    k = int(-(-p*len(c) // 100))  # calculate the index of the p-th percentile
    return binary_search(c, k)  # use binary search to find the element at the index k


# -------------------------------------------
#    Test running functions 
# -------------------------------------------


def run_unit_tests():
    """Run a set of unit tests on the implementation of the percentile algorithm."""
    test_find_percentile([1],[],5,1)
    test_find_percentile([1],[],50,1)
    test_find_percentile([1,2,7,8,10],[6,12],50,7)
    test_find_percentile([1,2,7,8],[6,12],50,6)
    test_find_percentile([15,20,35,40,50],[],30,20)
    test_find_percentile([15,20],[25,40,50],40,20)
    test_find_percentile([10,20,30,40],[15,25,35,45,50],50,30)
    print('Unit tests passed successfully')


def run_stress_test(max_test_size=10, max_attempts=100, max_right_border=100):
    """Run a set of stress tests on the implementation of the percentile algorithm.
    
    Parameters:
    max_test_size (int): maximum size of the input arrays for the test cases.
    max_attempts (int): maximum number of attempts for each test case.
    max_right_border (int): maximum possible value for the elements in the input arrays.
    """
    seed(100)
    for test_size in range(max_test_size):
        print(f' - Stress test size: {test_size}')
        for right_border in range(max_right_border):
            for attempt in range(max_attempts):
                a = get_random_test(test_size, right_border)
                b = get_random_test(max_test_size - test_size - 1, right_border) 
                p = randint(1, 100)
                test_find_percentile(a, b, p, reference_solution(a, b, p))
    print('Stress tests passed successfully')


def run_max_test():
    """Run the algorithm with the largest possible input size and check if the output is correct."""
    seed(100)
    a = get_random_test(150000, 100000000)
    b = get_random_test(150000, 100000000)
    p = randint(1, 100)
    
    start_time = time()
    find_percentile(a, b, p)
    end_time = time()
    working_time = end_time - start_time
    
    test_find_percentile(a, b, p, reference_solution(a, b, p))
    print(f' - Solution working time under max test load: {working_time:.6f} seconds')
    print('Max tests passed successfully')


# -------------------------------------------
#    Main program
# -------------------------------------------


def main():
    """Run the main program which executes the unit, stress and max tests."""
    run_unit_tests()
    run_stress_test()
    run_max_test()


if __name__ == "__main__":
    main()
