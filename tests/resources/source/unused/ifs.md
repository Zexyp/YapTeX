## positive
#if yeet_priority
yeet priority
#elif yes
yes
#else
no
#endif

### def
#ifdef def_yeet_priority
def yeet priority
#elifdef def_yes
def yes
#else
def no
#endif

## negative
#ifn yeet_priority
not yeet priority
#elif yes
not yes
#else
no
#endif

### def
#ifndef def_yeet_priority
not def yeet priority
#elifndef def_yes
not def yes
#else
def no
#endif

# compound

## def
#ifdef def_yeet_priority && def_yes
def both
#endif

#ifdef def_yeet_priority || def_yes
or
#endif

#ifdef !def_yeet_priority
def neg
#endif