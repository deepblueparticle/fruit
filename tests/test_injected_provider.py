#!/usr/bin/env python3
#  Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from nose2.tools import params

from fruit_test_common import *

COMMON_DEFINITIONS = '''
    #include <fruit/fruit.h>
    #include <vector>
    #include "test_macros.h"

    struct Annotation1 {};
    struct Annotation2 {};
    '''

def test_error_non_class_type_parameter():
    source = '''
        struct X {};

        fruit::Provider<X*> provider;
        '''
    expect_compile_error(
        'NonClassTypeError<X\*,X>',
        'A non-class type T was specified. Use C instead',
        COMMON_DEFINITIONS,
        source)

def test_error_annotated_type_parameter():
    source = '''
        struct X {};

        using XAnnot = fruit::Annotated<Annotation1, X>;

        fruit::Provider<XAnnot> provider;
        '''
    expect_compile_error(
        'AnnotatedTypeError<fruit::Annotated<Annotation1,X>,X>',
        'An annotated type was specified where a non-annotated type was expected.',
        COMMON_DEFINITIONS,
        source)

@params(
    ('X', 'fruit::Provider<X>'),
    ('fruit::Annotated<Annotation1, X>', 'fruit::Annotated<Annotation1, fruit::Provider<X>>'))
def test_get_ok(XAnnot, XProviderAnnot):
    source = '''
        bool x_constructed = false;

        struct X {
          using Inject = X();
          X() {
            x_constructed = true;
          }
        };

        fruit::Component<XAnnot> getComponent() {
          return fruit::createComponent();
        }

        int main() {
          fruit::Injector<XAnnot> injector(getComponent());
          fruit::Provider<X> provider = injector.get<XProviderAnnot>();

          Assert(!x_constructed);

          X& x = provider.get<X&>();
          (void)x;

          Assert(x_constructed);
        }
        '''
    expect_success(
        COMMON_DEFINITIONS,
        source,
        locals())

def test_get_during_injection_ok():
    source = '''
        struct X {
          INJECT(X()) = default;
          void foo() {
          }
        };

        struct Y {
          X x;
          INJECT(Y(fruit::Provider<X> xProvider))
            : x(xProvider.get<X>()) {
          }

          void foo() {
            x.foo();
          }
        };

        struct Z {
          Y y;
          INJECT(Z(fruit::Provider<Y> yProvider))
              : y(yProvider.get<Y>()) {
          }

          void foo() {
            y.foo();
          }
        };

        fruit::Component<Z> getZComponent() {
          return fruit::createComponent();
        }

        int main() {
          fruit::Injector<Z> injector(getZComponent());
          fruit::Provider<Z> provider(injector);
          // During provider.get<Z>(), yProvider.get() is called, and during that xProvider.get()
          // is called.
          Z z = provider.get<Z>();
          z.foo();
        }
        '''
    expect_success(
        COMMON_DEFINITIONS,
        source)

def test_get_error_type_not_provided():
    source = '''
        struct X {};
        struct Y {};

        void f(fruit::Provider<X> provider) {
          provider.get<Y>();
        }
        '''
    expect_compile_error(
        'TypeNotProvidedError<Y>',
        'Trying to get an instance of T, but it is not provided by this Provider/Injector.',
        COMMON_DEFINITIONS,
        source)

def test_get_error_type_pointer_pointer_not_provided():
    source = '''
        struct X {};

        void f(fruit::Provider<X> provider) {
          provider.get<X**>();
        }
        '''
    expect_compile_error(
        'TypeNotProvidedError<X\*\*>',
        'Trying to get an instance of T, but it is not provided by this Provider/Injector.',
        COMMON_DEFINITIONS,
        source)

@params(
    ('fruit::Provider<Y>'),
    ('ANNOTATED(Annotation1, fruit::Provider<Y>)'))
def test_lazy_injection_with_annotations(Y_PROVIDER_ANNOT):
    source = '''
        struct Y {
          using Inject = Y();
          Y() {
            Assert(!constructed);
            constructed = true;
          }

          static bool constructed;
        };

        bool Y::constructed = false;

        struct X {
          INJECT(X(Y_PROVIDER_ANNOT provider)) : provider(provider) {
            Assert(!constructed);
            constructed = true;
          }

          void run() {
            Y* y(provider);
            (void) y;
          }

          fruit::Provider<Y> provider;

          static bool constructed;
        };

        bool X::constructed = false;

        fruit::Component<X> getComponent() {
          return fruit::createComponent();
        }

        int main() {
          fruit::NormalizedComponent<> normalizedComponent(fruit::createComponent());
          fruit::Injector<X> injector(normalizedComponent, getComponent());

          Assert(!X::constructed);
          Assert(!Y::constructed);

          X* x(injector);

          Assert(X::constructed);
          Assert(!Y::constructed);

          x->run();

          Assert(X::constructed);
          Assert(Y::constructed);
        }
        '''
    expect_success(
        COMMON_DEFINITIONS,
        source,
        locals())

if __name__ == '__main__':
    import nose2
    nose2.main()
