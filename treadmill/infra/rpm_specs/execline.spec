Name: execline
Version: 2.2.0.0
Release: 12
Summary: Dependency for treadmill
Source0: execline-2.2.0.0.tar.gz
License: ISC
Group: TW
BuildRoot: %{_tmppath}/%{name}-buildroot
%description
Write some descripton about your package.
%prep
%setup -q
%build
./configure --prefix=/opt/s6 --with-include=/opt/s6/include --with-lib=/opt/s6/lib/skalibs
make
%install
make install
install -m 700 -d $RPM_BUILD_ROOT/opt/s6/bin
install -m 700 -d $RPM_BUILD_ROOT/opt/s6/lib/execline
install -m 700 -d $RPM_BUILD_ROOT/opt/s6/include/execline
install -m 700 background $RPM_BUILD_ROOT/opt/s6/bin/background
install -m 700 backtick $RPM_BUILD_ROOT/opt/s6/bin/backtick
install -m 700 define $RPM_BUILD_ROOT/opt/s6/bin/define
install -m 700 dollarat $RPM_BUILD_ROOT/opt/s6/bin/dollarat
install -m 700 elgetopt $RPM_BUILD_ROOT/opt/s6/bin/elgetopt
install -m 700 elgetpositionals $RPM_BUILD_ROOT/opt/s6/bin/elgetpositionals
install -m 700 elglob $RPM_BUILD_ROOT/opt/s6/bin/elglob
install -m 700 emptyenv $RPM_BUILD_ROOT/opt/s6/bin/emptyenv
install -m 700 exec $RPM_BUILD_ROOT/opt/s6/bin/exec
install -m 700 execlineb $RPM_BUILD_ROOT/opt/s6/bin/execlineb
install -m 700 exit $RPM_BUILD_ROOT/opt/s6/bin/exit
install -m 700 export $RPM_BUILD_ROOT/opt/s6/bin/export
install -m 700 fdblock $RPM_BUILD_ROOT/opt/s6/bin/fdblock
install -m 700 fdclose $RPM_BUILD_ROOT/opt/s6/bin/fdclose
install -m 700 fdmove $RPM_BUILD_ROOT/opt/s6/bin/fdmove
install -m 700 fdswap $RPM_BUILD_ROOT/opt/s6/bin/fdswap
install -m 700 fdreserve $RPM_BUILD_ROOT/opt/s6/bin/fdreserve
install -m 700 forbacktickx $RPM_BUILD_ROOT/opt/s6/bin/forbacktickx
install -m 700 foreground $RPM_BUILD_ROOT/opt/s6/bin/foreground
install -m 700 forstdin $RPM_BUILD_ROOT/opt/s6/bin/forstdin
install -m 700 forx $RPM_BUILD_ROOT/opt/s6/bin/forx
install -m 700 getcwd $RPM_BUILD_ROOT/opt/s6/bin/getcwd
install -m 700 getpid $RPM_BUILD_ROOT/opt/s6/bin/getpid
install -m 700 heredoc $RPM_BUILD_ROOT/opt/s6/bin/heredoc
install -m 700 homeof $RPM_BUILD_ROOT/opt/s6/bin/homeof
install -m 700 if $RPM_BUILD_ROOT/opt/s6/bin/if
install -m 700 ifelse $RPM_BUILD_ROOT/opt/s6/bin/ifelse
install -m 700 ifte $RPM_BUILD_ROOT/opt/s6/bin/ifte
install -m 700 ifthenelse $RPM_BUILD_ROOT/opt/s6/bin/ifthenelse
install -m 700 import $RPM_BUILD_ROOT/opt/s6/bin/import
install -m 700 importas $RPM_BUILD_ROOT/opt/s6/bin/importas
install -m 700 loopwhilex $RPM_BUILD_ROOT/opt/s6/bin/loopwhilex
install -m 700 multidefine $RPM_BUILD_ROOT/opt/s6/bin/multidefine
install -m 700 multisubstitute $RPM_BUILD_ROOT/opt/s6/bin/multisubstitute
install -m 700 pipeline $RPM_BUILD_ROOT/opt/s6/bin/pipeline
install -m 700 piperw $RPM_BUILD_ROOT/opt/s6/bin/piperw
install -m 700 redirfd $RPM_BUILD_ROOT/opt/s6/bin/redirfd
install -m 700 runblock $RPM_BUILD_ROOT/opt/s6/bin/runblock
install -m 700 shift $RPM_BUILD_ROOT/opt/s6/bin/shift
install -m 700 trap $RPM_BUILD_ROOT/opt/s6/bin/trap
install -m 700 tryexec $RPM_BUILD_ROOT/opt/s6/bin/tryexec
install -m 700 unexport $RPM_BUILD_ROOT/opt/s6/bin/unexport
install -m 700 withstdinas $RPM_BUILD_ROOT/opt/s6/bin/withstdinas
install -m 744 libexecline.a.xyzzy $RPM_BUILD_ROOT/opt/s6/lib/execline/libexecline.a
install -m 744 src/include/execline/config.h $RPM_BUILD_ROOT/opt/s6/include/execline/config.h
%post
%files
/opt/s6/bin/background
/opt/s6/bin/backtick
/opt/s6/bin/define
/opt/s6/bin/dollarat
/opt/s6/bin/elgetopt
/opt/s6/bin/elgetpositionals
/opt/s6/bin/elglob
/opt/s6/bin/emptyenv
/opt/s6/bin/exec
/opt/s6/bin/execlineb
/opt/s6/bin/exit
/opt/s6/bin/export
/opt/s6/bin/fdblock
/opt/s6/bin/fdclose
/opt/s6/bin/fdmove
/opt/s6/bin/fdswap
/opt/s6/bin/fdreserve
/opt/s6/bin/forbacktickx
/opt/s6/bin/foreground
/opt/s6/bin/forstdin
/opt/s6/bin/forx
/opt/s6/bin/getcwd
/opt/s6/bin/getpid
/opt/s6/bin/heredoc
/opt/s6/bin/homeof
/opt/s6/bin/if
/opt/s6/bin/ifelse
/opt/s6/bin/ifte
/opt/s6/bin/ifthenelse
/opt/s6/bin/import
/opt/s6/bin/importas
/opt/s6/bin/loopwhilex
/opt/s6/bin/multidefine
/opt/s6/bin/multisubstitute
/opt/s6/bin/pipeline
/opt/s6/bin/piperw
/opt/s6/bin/redirfd
/opt/s6/bin/runblock
/opt/s6/bin/shift
/opt/s6/bin/trap
/opt/s6/bin/tryexec
/opt/s6/bin/unexport
/opt/s6/bin/withstdinas
/opt/s6/lib/execline/libexecline.a
/opt/s6/include/execline/config.h
