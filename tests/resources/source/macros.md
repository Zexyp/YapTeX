#set variable="value"

#define HELLO_WORLD Hello World
#define MULTILINE upsík\
dupsík
#define ARGED(YEET) %YEET
#define ARGED2(YEET; X) %YEET - %X

?HELLO_WORLD
?MULTILINE

?ARGED(poopsie)
?ARGED(%variable)
?ARGED2(poopsie; 2)

#undef HELLO_WORLD
