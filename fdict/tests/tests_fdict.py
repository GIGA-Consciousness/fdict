# Unit testing of fdict
from fdict import fdict, sfdict

def test_fdict_creation():
    '''fdict: Test creation of just a nested dict, without anything else'''
    a = fdict()
    a['c']['b'] = set([1, 2])
    assert a == {'c/b': set([1, 2])}

def test_fdict_basic():
    '''fdict: Basic tests + copy test'''
    a = fdict()
    a['a'] = {}
    a['c']['b'] = set([1, 2])

    assert a.keys() == ['c/b']
    assert a.items() == [('c/b', set([1, 2]))]

    # Copy test
    acopy = a.copy()
    assert acopy.items() == a.items()
    assert acopy is not a

    # Referencing into another variable of a nested item + check update of nested items
    b = acopy['c']
    assert b.items() == [('b', set([1, 2]))]
    acopy['c'].update({'d': 3})
    assert acopy == {'c/b': set([1, 2]), 'c/d': 3}
    assert b == {'b': set([1, 2]), 'd': 3}

    # Other tests
    d = fdict()
    d['b'] = {'a': 1} # test subitem assignment of a dict
    d['c/b'] = set([2, 3, 5])
    assert d.to_dict() == {'c/b': set([2, 3, 5]), 'b/a': 1}

    a.update(d)
    assert a.to_dict() == {'c/b': set([2, 3, 5]), 'b/a': 1}
    assert a['c'].to_dict() == {'b': set([2, 3, 5])}

def test_sfdict_basic():
    '''sfdict: basic tests'''
    # Sfdict test
    g = sfdict(filename='testshelf')
    g['a'] = 3
    g['b/c'] = set([1, 3, 4])
    g['d'] = {}
    assert g == {'a': 3, 'b/c': set([1, 3, 4])}
    assert g == {'a': 3, 'b/c': set([1, 3, 4]), 'd': {}} # empty dicts are stripped out before comparison
    assert g['b'].filename == g.filename # check that subdicts also share the same filename (parameters propagation)

    # Sfdict reloading test
    h = sfdict(filename='testshelf')
    assert h == g
    g.close()
    h.close()

    # Flattening test
    m = {}
    m['a'] = 1
    m['b'] = {'c': 3, 'd': {'e': 5}}
    m['f'] = set([1, 2, 5])
    m2 = fdict(m)
    assert dict(m2.items()) == fdict.flatkeys(m)

    # Update and extract test
    n = {}
    n['b'] = {'d': {'f': 6}}
    n['g'] = 7
    m2.update(n)
    assert m2 == {'a': 1, 'g': 7, 'b/c': 3, 'b/d/e': 5, 'b/d/f': 6, 'f': set([1, 2, 5])}

    assert m2['b'].d == m2.d
    assert m2['b'].extract().d == {'b/c': 3, 'b/d/e': 5, 'b/d/f': 6}

    # len() test
    assert len(m2) == 6
    assert len(m2['b']) == 3
    assert len(m2['b']['d']) == len(m2['b/d']) == 2
    assert not hasattr(m2['g'], '__len__') and isinstance(m2['g'], int)

def test_fdict_extract():
    '''Extract extended test'''
    a10 = fdict()
    a10['c/b/d'] = set([1, 2])
    assert a10['c'].extract(fullpath=True).d == {'c/b/d': {1, 2}}
    assert a10['c'].extract(fullpath=True) == {'b/d': {1, 2}}
    assert a10['c'].extract(fullpath=False).d == {'b/d': {1, 2}}

    # Contains test
    p=fdict()
    p['a/b/c'] = set([1, 2])
    p['a/c'] = 3
    p['a/d'] = {'e': {'f': 4}, 'g': 5}
    p['h'] = 6
    assert 'h' in p # check existence of a leaf (O(1))
    assert 'a/b/c' in p # check existence of a nested leaf (O(1))
    assert 'a/b' in p # check existence of a nested dict (O(n))

    # Del test
    p=fdict()
    p['a/b/c'] = set([1, 2])
    p['a/c'] = 3
    p['a/d'] = {'e': {'f': 4}, 'g': 5}
    p['h'] = 6
    p2 = p.copy()
    assert 'h' in p # check existence of a leaf (O(1))
    assert 'a/b/c' in p # check existence of a nested leaf (O(1))
    assert 'a/b' in p # check existence of a nested dict (O(n))
    del p['a/b/c']
    del p2['a']['b']['c']  # test both types of access (fullpath or by subselection)
    assert p == p2 == {'h': 6, 'a/d/e/f': 4, 'a/c': 3, 'a/d/g': 5}
    del p['h']
    del p2['h']
    assert p == p2 == {'a/d/e/f': 4, 'a/c': 3, 'a/d/g': 5}
    del p['a/d']
    del p2['a']['d']
    assert p == p2 == {'a/c': 3}
    try:
        # Delete inexistent key
        del p['a']['b']['x']
    except KeyError as exc:
        assert True
    else:
        assert False

def test_fdict_update_eq():
    '''Update test and equality test'''
    a1 = {'a': set([1, 2]), 'b': {'c': 3, 'c2': 4}, 'd': 4}
    b1 = {'a': set([1, 2, 3]), 'b': {'c': 4, 'c3': 3}, 'e': 5}
    a2 = fdict(a1)
    b2 = fdict(b1)
    a11 = a1.copy()
    a12 = a1.copy()
    a13 = a1.copy()
    a14 = a1.copy()
    a15 = a1.copy()
    a21 = a2.copy()
    a22 = a2.copy()
    a23 = a2.copy()
    a24 = a2.copy()
    a25 = a2.copy()

    # no rootpath (ie, use whole dicts)
    a11.update(b1)
    a21.update(b2)
    assert a11 == {'a': set([1, 2, 3]), 'b': {'c3': 3, 'c': 4}, 'e': 5, 'd': 4}
    assert a21 == {'a': set([1, 2, 3]), 'b/c': 4, 'b/c2': 4, 'b/c3': 3, 'e': 5, 'd': 4} # by default, fdict supports recursive update (eg, c2 is kept here)

    # update a subdict with a subdict
    a12['b'].update(b1['b'])
    a22['b'].update(b2['b'])
    assert a12 == {'a': set([1, 2]), 'b': {'c3': 3, 'c2': 4, 'c': 4}, 'd': 4}
    assert a22 == {'a': set([1, 2]), 'b/c': 4, 'b/c2': 4, 'b/c3': 3, 'd': 4}
    assert a22 == a12
    assert len(a22) == 5 # len() test

    # update of a subdict with a whole dict (extracted subdict)
    a13['b'].update(b1['b'])
    b2sub = b2['b'].extract()
    a23['b'].update(b2sub)
    b2sub == {'c': 4, 'c3': 3}
    assert b2sub == {'c': 4, 'c3': 3}
    assert a23 == a22
    assert b2['b'].rootpath == b2sub.rootpath # rootpath is kept after extract
    assert b2['b'].d == b2.d # dict of a sub fdict is the same as the root fdict's dict
    assert dict(b2['b'].items()) == dict(b2sub.items())
    assert dict(b2['b'].items(fullpath=True)) == dict(b2sub.items(fullpath=True)) == b2sub.d # but the items (filtered by rootpath) will be different

    # update of a subdict with a whole dict (REALLY extracted subdict, rootpath is lost, so it is just like a new fdict)
    a14['b'].update(b1['b'])
    b2sub_orig = b2['b'].extract(fullpath=False)
    for b2sub in [b2sub_orig.to_dict(), b2sub_orig]:
        # This test should pass with both a dict and a fdict
        a24c = a24.copy()
        a24c['b'].update(b2sub)
        b2sub == {'c': 4, 'c3': 3}
        assert b2sub == {'c': 4, 'c3': 3}
        assert a24c == a22
        assert b2['b'].rootpath == 'b'
        assert not b2sub_orig.rootpath # rootpath is lost after extract(fullpath=False) (so it is like creating a new fdict)
        assert b2['b'].d == b2.d # dict of a sub fdict is the same as the root fdict's dict
        assert dict(b2['b'].items()) == dict(b2sub.items())
        assert dict(b2['b'].items(fullpath=False)) == dict(b2sub_orig.items(fullpath=True)) == b2sub_orig.d # but the items (filtered by rootpath) will be different

    # update of whole dict (extracted subdict) with subdict
    a15sub = a15['b']
    a15sub.update(b1['b'])
    a25sub = a25['b'].extract(fullpath=False)
    a25subc = a25sub.copy()
    a25sub.update(b2['b'])
    a25subc.update(b2['b'].extract(fullpath=False))
    assert a15sub == a25sub == a25subc
    assert a15sub.items() == a25sub.items() == a25subc.items()

def test_fdict_setitem_replacement():
    '''Test emptying by setitem to empty dict and singleton replacement by a nested dict'''
    a = fdict({'a/b': 1, 'a/c': set([1,2,3]), 'd': [1, 2, 3], 'e': [1, 2, 3]})
    # emptying by setitem with empty dict
    a['d'] = {}
    assert a == {'a/c': set([1, 2, 3]), 'a/b': 1, 'e': [1, 2, 3]}
    # replace singleton with a dict
    a['e'] = {'f': 2, 'g': 3}
    assert a == {'a/c': set([1, 2, 3]), 'a/b': 1, 'e/g': 3, 'e/f': 2}
    # replace dict with a singleton (does not work, both will coexist)
    a['a'] = 2
    assert a == {'a': 2, 'a/c': set([1, 2, 3]), 'a/b': 1, 'e/g': 3, 'e/f': 2}

def test_fdict_todictnested():
    '''Test to_dict_nested() conversion'''
    a = fdict({'a/b': 1, 'a/c': set([1, 2]), 'd': 3})
    adict = a.to_dict_nested()
    assert adict == {'a': {'b': 1, 'c': {1, 2}}, 'd': 3}
    assert not isinstance(adict, fdict) and isinstance(adict, dict)

def test_fdict_update_with_empty_dict():
    '''Test update of empty subdict'''
    a = fdict()
    a['a'] = {}
    a['a'].update({'b': 1, 'c': 2})
    assert a == {'a/c': 2, 'a/b': 1}

def test_fdict_fastview_basic():
    '''Test fastview mode basic features'''
    a = fdict(fastview=True)
    a['a/b/c'] = 1
    a['a']['b']['d'] = 2
    a['a']['e']['f'] = 3
    a['a']['e']['g']['h'] = 4
    a['a']['e']['g']['i'] = 5

    assert a.d.items() == [('a/e/g/', set(['a/e/g/i', 'a/e/g/h'])), ('a/e/f', 3), ('a/e/', set(['a/e/g/', 'a/e/f'])), ('a/', set(['a/e/', 'a/b/'])), ('a/b/c', 1), ('a/b/d', 2), ('a/b/', set(['a/b/c', 'a/b/d'])), ('a/e/g/i', 5), ('a/e/g/h', 4)]
    assert a.items() == [('a/e/f', 3), ('a/b/c', 1), ('a/b/d', 2), ('a/e/g/i', 5), ('a/e/g/h', 4)]  # items() on a fastview fdict should hide the nodes (eg, 'a/b/') and only show leafs, so that behavior is comparable to a non-fastview fdict
    assert a['a']['e'].items() == [('g/i', 5), ('g/h', 4), ('f', 3)]
    assert a['a']['e'].items(fullpath=True) == [('a/e/g/i', 5), ('a/e/g/h', 4), ('a/e/f', 3)]  # test recursive fastview items()

    assert a['a']['e'].items(fullpath=True) == [('a/e/g/i', 5), ('a/e/g/h', 4), ('a/e/f', 3)]
    assert a['a']['e'].keys(fullpath=True) == ['a/e/g/i', 'a/e/g/h', 'a/e/f']
    assert set(a['a']['e'].values()) == set([5, 4, 3])
    assert set(a['a'].values()) == set([1, 2, 3, 4, 5])  # use set() when we do not case about order in a list
    assert a['j'].items() == []  # empty nested dict
    assert a['j'].keys() == []
    assert a['j'].values() == []

    # test fastview contains
    assert 'a' in a
    assert 'a/' in a
    assert 'a/e/g/h' in a
    assert 'g' in a['a']['e']
    assert 'g' in a['a/e']
    assert 'g/h' in a['a/e']
    assert not 'a/e/g/x' in a
    assert not 'x' in a

    # test fastview copy
    from copy import deepcopy
    assert a == {'a/e/g/': set(['a/e/g/i', 'a/e/g/h']), 'a/e/f': 3, 'a/e/': set(['a/e/g/', 'a/e/f']), 'a/': set(['a/e/', 'a/b/']), 'a/b/c': 1, 'a/b/d': 2, 'a/b/': set(['a/b/c', 'a/b/d']), 'a/e/g/i': 5, 'a/e/g/h': 4}
    a2 = a.copy()
    for k in a.d.keys():
        if k.endswith(a.delimiter):
            # all nodes should be copied as different objects
            assert id(a.d[k]) != id(a2.d[k])
    a3 = deepcopy(a)
    for k in a.d.keys():
        # with a deep copy, all items (not just nodes) should be copied as different objects
        if hasattr(a.d[k], '__len__'):  # compare only collections (because for scalars we can't know if Python caches, or at least I did not find how to check that)
            assert id(a.d[k]) != id(a3.d[k])  # could replace by equivalent: a.d[k] is not a3.d[k]
    # check that a is unchanged after copy
    assert a == {'a/e/g/': set(['a/e/g/i', 'a/e/g/h']), 'a/e/f': 3, 'a/e/': set(['a/e/g/', 'a/e/f']), 'a/': set(['a/e/', 'a/b/']), 'a/b/c': 1, 'a/b/d': 2, 'a/b/': set(['a/b/c', 'a/b/d']), 'a/e/g/i': 5, 'a/e/g/h': 4}

def test_fdict_fastview_del():
    '''Test fastview del'''
    a = fdict({'a/e/g/': set(['a/e/g/i', 'a/e/g/h']), 'a/e/f': 3, 'a/e/': set(['a/e/g/', 'a/e/f']), 'a/': set(['a/e/', 'a/b/']), 'a/b/c': 1, 'a/b/d': 2, 'a/b/': set(['a/b/c', 'a/b/d']), 'a/e/g/i': 5, 'a/e/g/h': 4}, fastview=True)
    a2 = a.copy()
    # leaf deletion
    assert a['a'].keys(fullpath=True, nodes=True) == ['a/e/', 'a/e/g/', 'a/b/', 'a/b/c', 'a/b/d', 'a/e/f', 'a/e/g/i', 'a/e/g/h']
    del a['a/e/g/h']
    del a2['a']['e']['g']['h']
    assert a == a2 == {'a/e/g/': set(['a/e/g/i']), 'a/e/f': 3, 'a/e/': set(['a/e/g/', 'a/e/f']), 'a/': set(['a/e/', 'a/b/']), 'a/b/c': 1, 'a/b/d': 2, 'a/b/': set(['a/b/c', 'a/b/d']), 'a/e/g/i': 5}
    assert 'a/e/g/h' not in a['a'].keys(fullpath=True, nodes=True)
    # node deletion
    assert a['a/e'].keys() == a2['a']['e'].keys() == ['g/i', 'f']
    assert a['a/e'].keys(nodes=True) == a['a']['e'].keys(nodes=True) == ['g/', 'g/i', 'f']
    del a['a/e']
    del a2['a']['e']
    assert a == a.d == a2 == a2.d == {'a/': set(['a/b/']), 'a/b/c': 1, 'a/b/d': 2, 'a/b/': set(['a/b/c', 'a/b/d'])}
    assert not a['a/e'].keys() and not a2['a']['e']
    assert a['a'].keys(fullpath=True, nodes=True) == ['a/b/', 'a/b/d', 'a/b/c']

def test_fdict_metadata_nested_dict():
    '''Test fastview nodes metadata creation with nested dicts and at creation'''
    a = fdict({'a/b': 1, 'a/c': set([1,2,3]), 'd': [1, 2, 3]}, fastview=True)
    # add nested dict
    a['g'] = {'h': {'i': {'j': 6}, 'k': 7}, 'l': 8}
    assert a.d == {'g/l': 8, 'g/h/i/j': 6, 'g/h/i/': set(['g/h/i/j']), 'a/': set(['a/b', 'a/c']), 'a/c': set([1, 2, 3]), 'a/b': 1, 'g/h/': set(['g/h/k', 'g/h/i/']), 'g/': set(['g/l', 'g/h/']), 'g/h/k': 7, 'd': [1, 2, 3]}

def test_fdict_setitem_noconflict_delitem():
    '''Test fastview setitem replacement of singleton by nested dict and inversely + delitem'''
    a = fdict({'a/b': 1, 'a/c': set([1,2,3]), 'd': [1, 2, 3]}, fastview=True)
    # singleton to nested dict
    a['d/e'] = 4
    a['d/f'] = 5
    assert ('d', [1, 2, 3]) not in a.viewitems(nodes=True)
    # nested dict to singleton
    a['a'] = 2
    # add nested dict (and check metadata creation for each parent of nested leaves in the nested dict)
    a['g'] = {'h': {'i': {'j': 6}, 'k': 7}, 'l': 8}
    assert a['a'] == 2
    # delitem singleton
    del a['g/h/i/j']
    assert a.d == {'a': 2, 'd/': set(['d/f', 'd/e']), 'g/l': 8, 'd/f': 5, 'd/e': 4, 'g/h/': set(['g/h/k']), 'g/': set(['g/l', 'g/h/']), 'g/h/k': 7}
    # delitem nested dict
    del a['d']
    assert a.d == {'a': 2, 'g/l': 8, 'g/h/': set(['g/h/k']), 'g/': set(['g/l', 'g/h/']), 'g/h/k': 7}
