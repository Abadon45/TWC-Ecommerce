from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
import json

from TWC.middleware import SubdomainSessionMiddleware
from onlinestore.context_processors import cart_items


class CartPersistenceTests(TestCase):
    def test_subdomain_middleware_does_not_replace_session_cookie_name(self):
        request = RequestFactory().get('/', HTTP_HOST='www.example.com')
        SessionMiddleware(lambda response: response)(request)
        original_cookie_name = getattr(request.session, 'cookie_name', None)

        SubdomainSessionMiddleware(lambda response: response).process_request(request)

        self.assertEqual(getattr(request.session, 'cookie_name', None), original_cookie_name)

    def test_cart_context_uses_session_snapshot_without_product_api(self):
        request = RequestFactory().get('/')
        SessionMiddleware(lambda response: response)(request)
        request.session['cart'] = {
            'sample-product': {
                'id': 'SKU-1',
                'name': 'Sample Product',
                'slug': 'sample-product',
                'shop': 'sample-shop',
                'price': 125,
                'quantity': 2,
                'image': None,
            }
        }
        request.session.save()

        context = cart_items(request)

        self.assertEqual(context['cart_items'], 2)
        self.assertEqual(context['total_cart_subtotal'], 250)
        self.assertEqual(len(context['order_products']['sample-shop']), 1)

    def test_address_submission_returns_shipping_totals(self):
        client = self.client
        client.cookies['userCart'] = json.dumps({
            'sample-product': {
                'id': 'SKU-1',
                'name': 'Sample Product',
                'slug': 'sample-product',
                'shop': 'sample-shop',
                'image': None,
                'quantity': 1,
                'price': 125,
                'barley_point': 0,
            }
        })

        response = client.get(
            '/cart/checkout/',
            {
                'full_name': 'Test User',
                'phone': '09171234567',
                'address': 'Test Address',
                'province': 'CAVITE',
                'city': 'Imus',
                'barangay': 'Test Barangay',
                'landmark': 'Near the shop',
                'message': '',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

        completion = client.get(
            '/cart/submit-checkout/',
            {'username': 'admin', 'payment_method': 'cod'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(completion.status_code, 200)
        self.assertTrue(completion.json()['local_completion'])
        self.assertIn('/cart/checkout/complete/', completion.json()['redirect_url'])
        self.assertEqual(completion.cookies['userCart']['max-age'], 0)

    def test_demo_completion_renders_local_thank_you_page_without_order_api(self):
        session = self.client.session
        session['ordered_items_by_shop'] = {
            'sample-shop': {
                'items': [{
                    'product': {
                        'id': 'SKU-1',
                        'name': 'Sample Product',
                        'shop': 'sample-shop',
                        'slug': 'sample-product',
                        'image': None,
                        'price': '125.00',
                        'barley_point': 0,
                    },
                    'quantity': 1,
                    'get_total': 125.0,
                }],
                'total_quantity': 1,
                'subtotal': 125.0,
                'shipping_fee': 0,
                'discount': 0,
                'cod_amount': 125.0,
            }
        }
        session['shipping_address'] = {'full_name': 'Demo User'}
        session.save()

        completion = self.client.get(
            '/cart/submit-checkout/',
            {'payment_method': 'xendit'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(completion.status_code, 200)
        self.assertTrue(completion.json()['local_completion'])
        self.assertTrue(completion.json()['demo_order'])

        thank_you = self.client.get('/cart/checkout/complete/')
        self.assertEqual(thank_you.status_code, 200)
        self.assertContains(thank_you, 'Thank you for your order!')
        self.assertContains(thank_you, 'Sample Product')

    def test_regular_form_completion_redirects_to_local_thank_you_page(self):
        session = self.client.session
        session['ordered_items_by_shop'] = {
            'sample-shop': {
                'items': [{
                    'product': {
                        'id': 'SKU-1',
                        'name': 'Sample Product',
                        'shop': 'sample-shop',
                        'slug': 'sample-product',
                        'image': None,
                        'price': '125.00',
                        'barley_point': 0,
                    },
                    'quantity': 1,
                    'get_total': 125.0,
                }],
                'total_quantity': 1,
                'subtotal': 125.0,
                'shipping_fee': 0,
                'discount': 0,
                'cod_amount': 125.0,
            }
        }
        session.save()

        completion = self.client.get('/cart/submit-checkout/')

        self.assertRedirects(completion, '/cart/checkout/complete/')
        thank_you = self.client.get(completion.url)
        self.assertContains(thank_you, 'Thank you for your order!')

    def test_completion_can_use_signed_checkout_snapshot(self):
        from django.core import signing

        snapshot = {
            'sample-shop': {
                'items': [{
                    'product': {
                        'id': 'SKU-1',
                        'name': 'Signed Sample Product',
                        'shop': 'sample-shop',
                        'slug': 'signed-sample-product',
                        'image': None,
                        'price': '125.00',
                        'barley_point': 0,
                    },
                    'quantity': 1,
                    'get_total': 125.0,
                }],
                'total_quantity': 1,
                'subtotal': 125.0,
                'shipping_fee': 0,
                'discount': 0,
                'cod_amount': 125.0,
            }
        }

        completion = self.client.get(
            '/cart/submit-checkout/',
            {'checkout_snapshot': signing.dumps(snapshot)},
        )

        self.assertRedirects(completion, '/cart/checkout/complete/')
        self.assertContains(
            self.client.get('/cart/checkout/complete/'),
            'Signed Sample Product',
        )
