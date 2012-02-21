Name:           jna
Version:        3.2.7
Release:        %mkrel 6
Summary:        Pure Java access to native libraries

Group:          Development/Java
License:        LGPLv2+
URL:            https://jna.dev.java.net/
# The source for this package was pulled from upstream's vcs. Use the
# following commands to generate the tarball:
#   svn export https://jna.dev.java.net/svn/jna/tags/%{version}/jnalib/ --username guest jna-%{version}
#   rm -rf jna-%{version}/dist/*
#   tar cjf ~/rpm/SOURCES/jna-%{version}.tar.bz2 jna-%{version}
Source0:        %{name}-%{version}.tar.bz2
Source1:	%{name}-pom.xml
# This patch is Fedora-specific for now until we get the huge
# JNI library location mess sorted upstream
Patch1:         jna-3.2.5-loadlibrary.patch
# The X11 tests currently segfault; overall I think the X11 JNA stuff is just a 
# Really Bad Idea, for relying on AWT internals, using the X11 API at all,
# and using a complex API like X11 through JNA just increases the potential
# for problems.
Patch2:         jna-3.2.4-tests-headless.patch
Patch3:         jna-3.2.7-javadoc.patch
# Build using GCJ javadoc
Patch4:         jna-3.2.7-gcj-javadoc.patch
# junit cames from rpm
Patch5:         jna-3.2.5-junit.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}

# We manually require libffi because find-requires doesn't work
# inside jars.
Requires:       java  >= 0:1.6.0
Requires:       jpackage-utils, libffi
Requires(post):	jpackage-utils
Requires(postun): jpackage-utils
BuildRequires:  java-devel >= 0:1.6.0
BuildRequires:  jpackage-utils, libffi-devel
BuildRequires:  ant, ant-junit, ant-nodeps, ant-trax, junit
BuildRequires:  libx11-devel, libxt-devel


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
Requires:       %{name} = %{version}-%{release}


%description    javadoc
This package contains the javadocs for %{name}.


%package        contrib
Summary:        Contrib for %{name}
Group:          Development/Java
Requires:       %{name} = %{version}-%{release}
Obsoletes:      %{name}-examples


%description    contrib
This package contains the contributed examples for %{name}.


%prep
%setup -q -n %{name}-%{version}
sed -e 's|@JNIPATH@|%{_libdir}/%{name}|' %{PATCH1} | patch -p1
%patch2 -p1 -b .tests-headless
%patch3 -p1 -b .javadoc
# temporary hach for patch3 on epel5
chmod -Rf a+rX,u+w,g-w,o-w .
%patch4 -p0 -b .gcj-javadoc
%patch5 -p1 -b .junit
cp %{SOURCE1} ./

# UnloadTest fail during build since we modify class loading
rm test/com/sun/jna/JNAUnloadTest.java
# current bug: https://jna.dev.java.net/issues/show_bug.cgi?id=155
rm test/com/sun/jna/DirectTest.java

# all java binaries must be removed from the sources
#find . -name '*.jar' -delete
rm lib/junit.jar
find . -name '*.class' -delete

# remove internal copy of libffi
rm -rf native/libffi

# clean LICENSE.txt
sed -i 's/\r//' LICENSE.txt
chmod 0644 LICENSE.txt


%build
# We pass -Ddynlink.native which comes from our patch because
# upstream doesn't want to default to dynamic linking.
ant -Dcflags_extra.native="%{optflags}" -Ddynlink.native=true -Dnomixedjar.native=true jar contrib-jars javadoc
# remove compiled contribs
find contrib -name build -exec rm -rf {} \; || :
sed -i "s/VERSION/%{version}/" %{name}-pom.xml

%install
rm -rf %{buildroot}

# jars
install -D -m 644 build*/%{name}.jar %{buildroot}%{_javadir}/%{name}-%{version}.jar
(cd %{buildroot}%{_javadir}/; for jar in `ls *-%{version}.jar`; do ln -s $jar `echo $jar | sed -e 's/-%{version}//'`; done)
install -d -m 755 %{buildroot}%{_javadir}/%{name}
find contrib -name '*.jar' -exec cp {} %{buildroot}%{_javadir}/%{name}/ \;
# NOTE: JNA has highly custom code to look for native jars in this
# directory.  Since this roughly matches the jpackage guidelines,
# we'll leave it unchanged.
install -d -m 755 %{buildroot}%{_libdir}/%{name}
install -m 755 build*/native/libjnidispatch*.so %{buildroot}%{_libdir}/%{name}/

# install maven pom file
install -Dm 644 %{name}-pom.xml %{buildroot}%{_mavenpomdir}/JPP.%{name}.pom
# ... and maven depmap
%add_to_maven_depmap net.java.dev.jna %{name} %{version} JPP %{name}

# javadocs
install -p -d -m 755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -a doc/javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}

%clean
rm -rf %{buildroot}


%post
%update_maven_depmap


%postun
%update_maven_depmap


%files
%defattr(-,root,root,-)
%doc LICENSE.txt release-notes.html 
%{_libdir}/%{name}
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%{_mavenpomdir}/*.pom
%{_mavendepmapfragdir}/%{name}


%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}-%{version}


%files contrib
%defattr(-,root,root,-)
%{_javadir}/%{name}


