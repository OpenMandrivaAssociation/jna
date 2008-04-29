Name:           jna
Version:        3.0.2
Release:        %mkrel 0.7.2
Summary:        Pure Java access to native libraries

Group:          Development/Java
License:        LGPLv2+
URL:            https://jna.dev.java.net/
# The source for this package was pulled from upstream's vcs. Use the
# following commands to generate the tarball:
#   svn export https://jna.dev.java.net/svn/jna/tags/%{version}/jnalib/ --username guest jna-%{version}
#   tar -cjf jna-%{version}.tar.bz2 jna-%{version}
Source0:        %{name}-%{version}.tar.bz2
# https://jna.dev.java.net/issues/show_bug.cgi?id=60
Patch0:         jna-3.0.2-dynlink-and-cflags.patch
# This patch is Fedora-specific for now until we get the huge
# JNI library location mess sorted upstream
Patch1:         jna-3.0.2-loadlibrary.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:  java-rpmbuild >= 1.6 ant jpackage-utils ant-nodeps
BuildRequires:  libx11-devel libxt-devel libffi-devel
Obsoletes: jna-examples

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
%patch0 -p1
sed -e 's|@JNIPATH@|%{_libdir}/%{name}|' %{PATCH1} | patch -p1

# all java binaries must be removed from the sources
find . -name '*.jar' -exec rm -f '{}' \;
find . -name '*.class' -exec rm -f '{}' \;

# remove internal copy of libffi
rm -rf native/libffi

# remove random unused zips
rm dist/{src,doc}.zip

# clean LICENSE.txt
sed -i 's/\r//' LICENSE.txt
chmod 0644 LICENSE.txt

%build
# We pass -Ddynlink.native which comes from our patch because
# upstream doesn't want to default to dynamic linking.
%ant jar -Dcflags_extra.native="%{optflags}" -Ddynlink.native=true -Dnomixedjar.native=true
%ant javadoc


%install
rm -rf %{buildroot}

# jars
install -D -m 644 build/%{name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir}/; for jar in `ls *-%{version}.jar`; do ln -s $jar `echo $jar | sed -e 's/-%{version}//'`; done)
# NOTE: JNA has highly custom code to look for native jars in this
# directory.  Since this roughly matches the jpackage guidelines,
# we'll leave it unchanged.
install -d -m 755 %{buildroot}%{_libdir}/%{name}
install -m 755 build/native/libjnidispatch*.so %{buildroot}%{_libdir}/%{name}/

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
%{_javadir}/*.jar

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}
 
