Name:           jna
Version:        3.0.9
Release:        %mkrel 1
Summary:        Pure Java access to native libraries

Group:          Development/Java
License:        LGPLv2+
URL:            https://jna.dev.java.net/
# The source for this package was pulled from upstream's vcs. Use the
# following commands to generate the tarball:
#   svn export https://jna.dev.java.net/svn/jna/tags/%{version}/jnalib/ --username guest jna-%{version}
#   rm dist/*
#   tar -cjf jna-%{version}.tar.bz2 jna-%{version}
Source0:        %{name}-%{version}.tar.bz2
# This patch is Fedora-specific for now until we get the huge
# JNI library location mess sorted upstream
Patch1:         jna-3.0.2-loadlibrary.patch
# The X11 tests currently segfault; overall I think the X11 JNA stuff is just a 
# Really Bad Idea, for relying on AWT internals, using the X11 API at all,
# and using a complex API like X11 through JNA just increases the potential
# for problems.
Patch2:         jna-tests-headless.patch
# https://jna.dev.java.net/issues/show_bug.cgi?id=90
Patch3:         jna-3.0.4-nativemapped-array.patch
# Not yet sent upstream - haven't decided whether it's a good idea yet,
# but keeping around here for now.
Patch5:         jna-callback-exception.patch
# https://jna.dev.java.net/issues/show_bug.cgi?id=95
Patch6:		jna-3.0.9-linux-nomaplibrary.patch
# https://jna.dev.java.net/issues/show_bug.cgi?id=98
Patch7:         jna-3.0.9-processopen.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:  java-devel >= 1.6 ant jpackage-utils ant-nodeps
BuildRequires:  libx11-devel libxt-devel libffi-devel
BuildRequires:  java-rpmbuild >= 0:1.5.32
# We manually require libffi because find-requires doesn't work
# inside jars.
Requires:       java >= 0:1.6.0 jpackage-utils

%description
JNA provides Java programs easy access to native shared libraries
(DLLs on Windows) without writing anything but Java code. JNA's
design aims to provide native access in a natural way with a
minimum of effort. No boilerplate or generated code is required.
While some attention is paid to performance, correctness and ease
of use take priority.

%package        javadoc
Summary:        Javadocs for %{name}
Group:          Development/Java

%description    javadoc
This package contains the javadocs for %{name}.


%prep
%setup -q -n %{name}-%{version}
sed -e 's|@JNIPATH@|%{_libdir}/%{name}|' %{PATCH1} | patch -p1
%patch2 -p1 -b .tests-headless
%patch3 -p1 -b .nativemapped-array
#%patch5 -p1 -b .callback-exception
%patch6 -p1 -b .linux-nomaplibrary
%patch7 -p1 -b .processopen

# all java binaries must be removed from the sources
find . -name '*.jar' -exec rm -f '{}' \;
find . -name '*.class' -exec rm -f '{}' \;

# remove internal copy of libffi
rm -rf native/libffi

# clean LICENSE.txt
sed -i 's/\r//' LICENSE.txt
chmod 0644 LICENSE.txt

%build
# We pass -Ddynlink.native which comes from our patch because
# upstream doesn't want to default to dynamic linking.
%ant jar -Dcflags_extra.native="%{optflags}" -Ddynlink.native=true -Dnomixedjar.native=true examples
%ant javadoc


%install
rm -rf %{buildroot}

# jars
install -D -m 644 build*/%{name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir}/; for jar in `ls *-%{version}.jar`; do ln -s $jar `echo $jar | sed -e 's/-%{version}//'`; done)
# NOTE: JNA has highly custom code to look for native jars in this
# directory.  Since this roughly matches the jpackage guidelines,
# we'll leave it unchanged.
install -d -m 755 %{buildroot}%{_libdir}/%{name}
install -m 755 build*/native/libjnidispatch*.so %{buildroot}%{_libdir}/%{name}/

# javadocs
%__install -d "%{buildroot}%{_javadocdir}"
%__cp -a doc/javadoc "%{buildroot}%{_javadocdir}/%{name}-%{version}"
(cd %{buildroot}%{_javadocdir} && %{__ln_s} %{name}-%{version} %{name})


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(0644,root,root,0755)
%doc LICENSE.txt
%{_libdir}/%{name}
%{_javadir}/*

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

