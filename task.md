Implement a backend API for a system to manage a category tree. Categories can be nested arbitrarily deep and contain the following fields: name, description, image. Categories can be created (in any place inside the tree), edited (changing the fields), deleted, and moved around in the tree. The API needs to be flexible in the way categories can be retrieved (individual categories, the entire list, by depth in the tree, by parent - be creative).


Additionally, two categories can be marked as similar. If category A is similar to category B, that implies that B is similar to A as well (similarity is bidirectional). The API needs to support the relevant operations to manage category similarity (CRUD).


The number of categories will be up to 2'000, the number of similar category-pairs will be up to 200'000 and the system should perform reasonably well within that assumption.


The focus when designing the module should be on:

Simple, reliable implementation.

Engineering that is "just-right" - not over engineered for the requirements, but having enough robustness.

The code should be easy to understand and maintain.

Clean is more important than fully-featured - make sure all the details are done right.

While the main way to access the system should be via API, some form of graphical interface is welcome. No custom engineering is required, for example the built-in Django Admin is sufficient.


Separately, write a script that outputs:

The longest similar category "rabbit hole" and the categories it's comprised of.

The categories in each "rabbit island".

A rabbit hole is defined as the shortest sequence to get from category A to category B by just visiting similar categories. For example:

There are categories A, B, C, D.

A is similar to B and D.

B is similar to C and D.

The rabbit hole from A to C is A -> B -> C, even if A -> B -> C -> D exists as a sequence of similar categories.

A rabbit island is defined as the set of categories that can be reached via rabbit holes. Two categories that cannot be reached via rabbit holes are in separate rabbit islands.
