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

@params(
    ('X', 'int'),
    ('fruit::Annotated<Annotation1, X>', 'fruit::Annotated<Annotation2, int>'))
def test_error_not_base(XAnnot, intAnnot):
    source = '''
        struct X {};

        fruit::Component<intAnnot> getComponent() {
          return fruit::createComponent()
            .bind<XAnnot, intAnnot>();
        }
        '''
    expect_compile_error(
        'NotABaseClassOfError<X,int>',
        'I is not a base class of C.',
        COMMON_DEFINITIONS,
        source,
        locals())

# TODO: maybe the error should include the annotation here.
@params('X', 'fruit::Annotated<Annotation1, X>')
def test_error_bound_to_itself(XAnnot):
    source = '''
        struct X {};

        fruit::Component<X> getComponent() {
          return fruit::createComponent()
            .bind<XAnnot, XAnnot>();
        }
        '''
    expect_compile_error(
        'InterfaceBindingToSelfError<X>',
        'The type C was bound to itself.',
        COMMON_DEFINITIONS,
        source,
        locals())

if __name__ == '__main__':
    import nose2
    nose2.main()
