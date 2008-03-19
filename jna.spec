Name:           jna
Version:        3.0
Release:        %mkrel 0.0.2
Epoch:          0
Summary:        Dynamically access native libraries from Java without JNI
License:        LGPL
URL:            https://jna.dev.java.net/
Source0:        https://jna.dev.java.net/source/browse/*checkout*/jna/trunk/jnalib/dist/src.zip
BuildRequires:  java-rpmbuild >= 0:1.6
BuildRequires:  ant
BuildRequires:  ant-nodeps
BuildRequires:  libx11-devel
Group:          Development/Java
Buildroot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
JNA provides Java programs easy access to native shared libraries (DLLs on
Windows) without writing anything but Java code?no JNI or native code is
required. This functionality is comparable to Windows' Platform/Invoke and
Python's ctypes. Access is dynamic at runtime without code generation.

JNA's design aims to provide native access in a natural way with a minimum of
effort. No boilerplate or generated code is required. While some attention is
paid to performance, correctness and ease of use take priority.

The JNA library uses a small native library stub to dynamically invoke native
code. The developer uses a Java interface to describe functions and structures
in the target native library. This makes it quite easy to take advantage of
native platform features without incurring the high overhead of configuring
and building JNI code for multiple platforms.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%package examples
Summary:	Examples for %{name}
Group:		Development/Java
Requires:	%{name} = %{version}-%{release}

%description javadoc
Javadoc for %{name}.

%description examples
Examples for %{name}.

%prep
%setup -q -c {name}
chmod 755 native/libffi/configure

%build
CLASSPATH="/usr/share/java/xalan-j2-serializer.jar" \
%ant -DARCH="$MAKE_ARCH" -DCC="%__cc" jar native javadoc examples

%install
%{__rm} -rf %{buildroot}
%__install -d "%{buildroot}%{_jnidir}"
%__install -m0644 build/linux-*.jar "%{buildroot}%{_jnidir}/%{name}-native-%{version}.jar"
%__ln_s "%{name}-%{version}.jar" "%{buildroot}%{_jnidir}/%{name}.jar"

%__install -d "%{buildroot}%{_javadir}"
%__install -m0644 build/jna.jar "%{buildroot}%{_javadir}/%{name}-%{version}.jar"
%__ln_s "%{name}-%{version}.jar" "%{buildroot}%{_javadir}/%{name}.jar"
%__install -m0644 build/examples.jar "%{buildroot}%{_javadir}/%{name}-examples-%{version}.jar"
%__ln_s "%{name}-examples-%{version}.jar" "%{buildroot}%{_javadir}/%{name}-examples.jar"

%__install -d "%{buildroot}%{_javadocdir}"
%__cp -a doc/javadoc "%{buildroot}%{_javadocdir}/%{name}-%{version}"
(cd %{buildroot}%{_javadocdir} && %{__ln_s} %{name}-%{version} %{name})

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(0644,root,root,0755)
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-%{version}.jar
%{_jnidir}/*.jar

%files examples
%{_javadir}/%{name}-examples.jar
%{_javadir}/%{name}-examples-%{version}.jar

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}
 
