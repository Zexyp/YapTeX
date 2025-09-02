#set num 0
#set file "directory<>space/file.png"
#set var "hello"
%var
%var:u
%var:l
%var:t
%file:html
%file:esc
%file:id
%file:bn
%file:dn

%file\:esc

#inc var
%var
#inc var
%var
#dec var
%var
#dec var
%var
#dec var
%var

#inc num
%num
#inc num
%num
#dec num
%num
#dec num
%num
#dec num
%num
#dec num
%num

%_YEAR_
%_MONTH_
%_DAY_
%__FILE__
%__LINE__
%__TIME__
%__DATE__
