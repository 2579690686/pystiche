import torch

from pystiche import pyramid
from pystiche.image import extract_edge_size
from pystiche.ops import PixelComparisonOperator
from pystiche.pyramid import level
from utils import PysticheTestCase


class TestLevel(PysticheTestCase):
    def test_Level_iter(self):
        edge_size = 1
        num_steps = 100
        edge = "short"

        pyramid_level = level.PyramidLevel(edge_size, num_steps, edge)

        actual = tuple(iter(pyramid_level))
        desired = tuple(range(1, num_steps + 1))
        self.assertTupleEqual(actual, desired)


class TestPyramid(PysticheTestCase):
    def test_ImagePyramid_build_levels_scalar_num_steps(self):
        num_levels = 3
        num_steps = 2

        pyramid_levels = pyramid.ImagePyramid([1] * num_levels, num_steps)

        actual = tuple([level.num_steps for level in pyramid_levels])
        desired = tuple([num_steps] * num_levels)
        self.assertTupleEqual(actual, desired)

    def test_ImagePyramid_build_levels_scalar_edge(self):
        num_levels = 3
        edge = "long"

        pyramid_levels = pyramid.ImagePyramid([1] * num_levels, 1, edge=edge)

        actual = tuple([level.edge for level in pyramid_levels])
        desired = tuple([edge] * num_levels)
        self.assertTupleEqual(actual, desired)

    def test_ImagePyramid_len(self):
        num_levels = 3

        image_pyramid = pyramid.ImagePyramid([1] * num_levels, [1] * num_levels)

        actual = len(image_pyramid)
        desired = num_levels
        self.assertEqual(actual, desired)

    def test_ImagePyramid_getitem(self):
        edge_sizes = (1, 2, 3)
        num_steps = (4, 5, 6)

        image_pyramid = pyramid.ImagePyramid(edge_sizes, num_steps)

        for idx, desired in enumerate(zip(edge_sizes, num_steps)):
            pyramid_level = image_pyramid[idx]
            self.assertIsInstance(pyramid_level, level.PyramidLevel)

            actual = (pyramid_level.edge_size, pyramid_level.num_steps)
            self.assertTupleEqual(actual, desired)

    def test_ImagePyramid_iter(self):
        edge_sizes = (1, 2, 3)
        num_steps = (4, 5, 6)

        image_pyramid = pyramid.ImagePyramid(edge_sizes, num_steps)

        desireds = zip(edge_sizes, num_steps)
        for pyramid_level, desired in zip(image_pyramid, desireds):
            self.assertIsInstance(pyramid_level, level.PyramidLevel)

            actual = (pyramid_level.edge_size, pyramid_level.num_steps)
            self.assertTupleEqual(actual, desired)

    def test_ImagePyramid_iter_resize(self):
        class TestOperator(PixelComparisonOperator):
            def target_image_to_repr(self, image):
                return image, None

            def input_image_to_repr(self, image, ctx):
                pass

            def calculate_score(self, input_repr, target_repr, ctx):
                pass

        edge_sizes = (32, 64)

        torch.manual_seed(0)
        image = torch.rand((1, 3, 128, 128))

        op = TestOperator()
        op.set_target_image(image)

        image_pyramid = pyramid.ImagePyramid(edge_sizes, 1, resize_targets=(op,))
        for pyramid_level, edge_size in zip(image_pyramid, edge_sizes):
            actual = extract_edge_size(op.target_image, pyramid_level.edge)
            desired = edge_size
            self.assertEqual(actual, desired)

    def test_ImagePyramid_iter_restore(self):
        class TestOperator(PixelComparisonOperator):
            def target_image_to_repr(self, image):
                return image, None

            def input_image_to_repr(self, image, ctx):
                pass

            def calculate_score(self, input_repr, target_repr, ctx):
                pass

        torch.manual_seed(0)
        size = (1, 3, 128, 128)
        image = torch.rand(*size)

        op = TestOperator()
        op.set_target_image(image)

        image_pyramid = pyramid.ImagePyramid((1,), 1, resize_targets=(op,))
        try:
            for pyramid_level in image_pyramid:
                raise Exception
        except Exception:
            pass

        actual = op.target_image.size()
        desired = size
        self.assertTupleEqual(actual, desired)

    def test_OctaveImagePyramid(self):
        max_edge_size = 16
        min_edge_size = 2

        image_pyramid = pyramid.OctaveImagePyramid(
            max_edge_size, 1, min_edge_size=min_edge_size
        )
        self.assertEqual(len(image_pyramid), 4)

        for idx in range(len(image_pyramid)):
            actual = image_pyramid[idx].edge_size
            desired = 2 ** (idx + 1)
            self.assertEqual(actual, desired)

    def test_OctaveImagePyramid_num_levels(self):
        max_edge_size = 16
        num_levels = 3
        min_edge_size = 2

        image_pyramid = pyramid.OctaveImagePyramid(
            max_edge_size, 1, num_levels=num_levels, min_edge_size=min_edge_size
        )
        self.assertEqual(len(image_pyramid), 3)

        for idx in range(len(image_pyramid)):
            actual = image_pyramid[idx].edge_size
            desired = 2 ** (idx + 2)
            self.assertEqual(actual, desired)