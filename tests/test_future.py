from unittest import TestCase
from futures.utils import unawait
from futures.future import Future


class TestFuture(TestCase):

    def test_work(self):
        elements = Future(lambda: [1, 2])
        self.assertEqual(type(elements), Future)

    def test_before(self):
        elements = Future(lambda: [1, 2])
        pop = elements.pop
        self.assertEqual(type(pop), Future)

    def test_await(self):
        elements = Future(lambda: [1, 2, 3])
        output = unawait(elements)
        self.assertEqual(output, [1, 2, 3])

    def test_getattr(self):
        elements = Future(lambda: [1, 2, 3])
        pop = unawait(elements.pop)
        pop(0)
        output = unawait(elements)
        self.assertEqual(output, [2, 3])

    def test_call(self):
        elements = Future(lambda: [1, 2, 3])
        elements.pop(0)
        output = unawait(elements)
        self.assertEqual(output, [2, 3])

    def test_compare(self):
        num = Future(lambda: 5)
        min = num < 10
        minq1 = num <= 5
        minq2 = num <= 6
        max = num > 1
        maxq1 = num >= 5
        maxq2 = num >= 4
        equ = 5 == num
        nequ = num != 3
        self.assertTrue(unawait(minq1), 'Incorrect x <= x')
        self.assertTrue(unawait(minq2), 'Incorrect x <= x')
        self.assertTrue(unawait(min), 'Incorrect x < x')
        self.assertTrue(unawait(maxq1), 'Incorrect x >= x')
        self.assertTrue(unawait(maxq2), 'Incorrect x >= x')
        self.assertTrue(unawait(max), 'Incorrect x > x')
        self.assertTrue(unawait(equ), 'Incorrect x == x')
        self.assertTrue(unawait(nequ), 'Incorrect x != x')

    def test_convertions(self):
        real_list = [1, 2, 3]
        future_list = Future(lambda: real_list)
        string_list = str(future_list)
        repr_list = repr(future_list)
        bytes_list = bytes(future_list)
        self.assertEqual(string_list, str(real_list))
        self.assertEqual(repr_list, repr(real_list))
        self.assertEqual(bytes_list, bytes(real_list))

    def test_convertions_types(self):
        data = ((int, '123', 123), (float, '8.2', 8.2),
                (complex, '3+1j', 3 + 1j), (bool, 0, False))
        for (func, value, target) in data:
            future_value = Future(lambda: value)
            output = func(future_value)
            self.assertEqual(output, target)

    def test_unpack(self):
        obj = Future(lambda: [0, 1, 2, 3, 4, 5])
        a, b = obj[:2]
        self.assertTrue(isinstance(a, Future))
        self.assertTrue(isinstance(b, Future))
