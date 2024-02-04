# Protobase

[![Documentation Status](https://readthedocs.org/projects/protobase/badge/?version=latest)](https://protobase.readthedocs.io/en/latest/?badge=latest)

Protobase is a simple Python library designed to serve as a foundational element in the creation and composition of object classes. 

Protobase makes some default decisions that can be useful in some software projects, automates the implementation of recurring functions in our classes, and provides some interesting functionalities.

While it is true that the features provided by protobase can be compared to those offered by standard dataclasses, the motivation for the development of this project is to achieve immutable and consignable objects in Python.

The development of this library is part of a larger personal project (Axis lang) and at this time I do not recommend its widespread use. While protobase has a test battery, this library is not being used by NASA. 

Protobase makes use of metaclasses, this can complicate things if we need our classes to extend from third party classes. The decision to use metaclasses may be relaxed in the future if this project could be interesting for the community.

## Basic functionality
```python
from protobase import Obj, traits

# We create a new class that implements the most common traits.
class Site(Obj, *traits.Common):
	name: str
	url: str

# We can see that the __init__ function has been automatically 
# implemented for our class
github = Site(name="GitHub", url="www.github.com")
gitlab = Site(name="GitLab", url="www.gitlab.com")

# The __repr__ method has also been implemented.
print(github)
Site(name="GitHub", url="www.github.com") 

# The same for the equality checking methods __eq__ and __ne__.
assert github != gitlab

# we can also automatically have the implementation of 
# comparison methods, so we can order our objects.
assert list(sorted([gitlab, github])) == [github, gitlab]

# The __hash__ method is also automatically implemented.
hash(github)

# So our new objects can be present in a set.
sites = {github, gitlab}

# We can use our new objects as keys in a dict.
user_count_by_site = {
	github: 100_000_000,
	gitlab:  30_000_000,
}
```
We can see how, as with dataclasses, the attributes of our 
objects have been inferred from the annotations that we 
have made in the body of the class.

These attributes have been transformed into slot descriptors:
```python
print(Site.name)
# <member 'name' of 'Site' objects>
```
By default our objects do not allow the assignment of new attributes dynamically.
```python
github.comment = 'A place to store code'
# AttributeError: 'Site' object has no attribute 'comment'
```
protobase decided to disable this feature, so typical of dynamic languages like python, mainly for security and trust issues, but also to save memory and cpu resources.

> **_NOTE:_**  However, we can enable this feature by using the `traits.Dynamic` trait. This allows us to add any number of additional attributes to an instance at runtime. 

## Advanced functionalities

**Inmutable**:
In the implementation of some algorithms and in certain software architectures, it can be crucial to ensure that an object, once created, cannot change any of its properties.

This can allow sharing objects between different components of the architecture. This characteristic can compel the application of better design patterns in many instances. It can also force the adoption of event-driven programming paradigms or reactive programming.
```python
from protobase import Obj, traits

class Site(Obj, *traits.Common, traits.Immutable):
    name: str
    url: str

wikipedia = Site(name="Wikipedia", url="www.wikipedia.org")
wikipedia.url = "www.wikipedia.com"
# AttributeError: Cannot set attribute 'url'. Site is inmutable.
```

**Hash Consing**:
In some cases, it is important to ensure that there is only one instance of a class with a certain set of attributes. This can be useful in the implementation of caches, in the implementation of optimization algorithms or in the implementation of certain design patterns.

```python
from protobase import Obj, traits

class Site(Obj, *traits.Common, traits.Consed):
    name: str
    url: str

# The same object with the same attributes results in the same instance.
bitbucket_1 = Site(name="Bitbucket", url="www.bitbucket.com")

bitbucket_2 = Site(name="Bitbucket", url="www.bitbucket.com")

assert bitbucket_1 is bitbucket_2
```

**protomethods**:

## Philosophy and future

I have decided to publish this library to be able to use it in different projects in the future, with the intention of making Python a safer language, less prone to errors, and more efficient.

In the future, Protobase will:

 - Implement runtime checking of attribute types (in development mode) to ensure that typing is respected. This has many limitations in a language like Python, but I believe this feature can save a lot of time for many programmers (including myself).
 - Delve deeper into the use of advanced annotations. Protobase might end up providing an annotation system to:
   - Improve the documentation of class attributes.
   - Alter the behavior of protomethods concerning certain attributes.
 - Implement visitor patterns to transform, evaluate, unify, and reify structured data.
