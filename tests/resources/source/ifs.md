## vars
### positive
#if primary
if
#elif secondary
else
#else
else
#endif

### negative
#ifn primary
not if
#elifn secondary
not else
#else
else
#endif

## def
### positive 
#ifdef primary
def if
#elifdef secondary
def else
#else
def else
#endif

### negative
#ifndef def_primary
def not if
#elifndef def_secondary
def not else
#else
def else
#endif

### compound

#ifdef def_primary && def_secondary
def both
#endif

#ifdef def_primary || def_secondary
or
#endif

#ifdef !def_primary
neg
#endif

### constant

#ifdef true
true
#endif

#ifndef false
false
#endif
