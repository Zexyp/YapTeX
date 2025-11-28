#set num 0
#set file "directory<>space/file.png"
#set var "hello"

%var
%{var:u}
%{var:l}
%{var:t}

%{file:html}
%{file:esc}
%{file:slug}
%{file:bn}
%{file:dn}

%file:esc

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
