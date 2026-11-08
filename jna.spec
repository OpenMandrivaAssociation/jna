Name:		jna
Version:	5.19.1
Release:	1
# The native makefile strips libjnidispatch.so and does not emit DWARF.
%global debug_package %{nil}
Summary:	Java Native Access
Group:		Development/Java
License:	(LGPL-2.1-or-later OR Apache-2.0)
URL:		https://github.com/java-native-access/jna
Source0:	https://codeload.github.com/java-native-access/jna/tar.gz/refs/tags/%{version}#/jna-%{version}.tar.gz
# The previous build shipped javadoc and a contrib jar.
Obsoletes:	jna-javadoc < %{version}-%{release}
Obsoletes:	jna-contrib < %{version}-%{release}
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	make
BuildRequires:	pkgconfig(libffi)
BuildRequires:	clang

%description
Java Native Access calls native functions from Java without handwritten
JNI glue. libjnidispatch.so is built against the system libffi and
loaded from the system library path.

%prep
%setup -q
# The tag archive contains prebuilt jars and a private libffi tree.
rm -rf dist lib contrib www test native/libffi
sed -i \
	-e 's/String VERSION = "TEMPLATE";/String VERSION = "%{version}";/' \
	-e 's/String VERSION_NATIVE = "TEMPLATE";/String VERSION_NATIVE = "7.0.4";/' \
	src/com/sun/jna/Version.java
# Upstream defaults to unpacking a library from the jar. Use the system one.
sed -i 's/getProperty("jna.nosys", "true")/getProperty("jna.nosys", "false")/' \
	src/com/sun/jna/Native.java
# The makefile would record the relative build path as the SONAME.
sed -i 's/-Wl,-soname,$@/-Wl,-soname,libjnidispatch.so/g' native/Makefile
grep -F 'String VERSION = "%{version}";' src/com/sun/jna/Version.java
grep -F 'String VERSION_NATIVE = "7.0.4";' src/com/sun/jna/Version.java
grep -F 'getProperty("jna.nosys", "false")' src/com/sun/jna/Native.java
if grep -F -- '-Wl,-soname,$@' native/Makefile; then
	echo "soname still uses the target path" >&2
	exit 1
fi
grep -F -- '-Wl,-soname,libjnidispatch.so' native/Makefile
if [ -e native/libffi ] || [ -e dist ]; then
	echo "prebuilt or bundled sources are still present" >&2
	exit 1
fi

%build
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
mkdir -p build/classes build/native
find src -name '*.java' > sources.list
"$JAVA_HOME/bin/javac" --release 8 -encoding UTF-8 \
	-h build/native -d build/classes @sources.list
# Headers from javac -h have to stay in build/native. make clean deletes them.
make -C native \
	DYNAMIC_LIBFFI=true \
	CC=cc \
	JNA_JNI_VERSION=7.0.4 \
	CHECKSUM=5fb98531302accd485c534c452dd952a \
	../build/native/libjnidispatch.so
cat > build/manifest.mf << EOF
Manifest-Version: 1.0
Main-Class: com.sun.jna.Native
Implementation-Title: com.sun.jna
Implementation-Vendor: JNA Development Team
Implementation-Version: %{version}
Specification-Title: Java Native Access (JNA)
Specification-Vendor: JNA Development Team
Specification-Version: %{version}
Automatic-Module-Name: com.sun.jna

EOF
"$JAVA_HOME/bin/jar" --create --manifest build/manifest.mf \
	--file build/jna.jar -C build/classes .
cat > build/jna.pom << EOF
<?xml version="1.0" encoding="UTF-8"?>
<project>
  <modelVersion>4.0.0</modelVersion>
  <groupId>net.java.dev.jna</groupId>
  <artifactId>jna</artifactId>
  <version>%{version}</version>
  <name>Java Native Access</name>
  <description>Java Native Access built against the system libffi.</description>
  <url>https://github.com/java-native-access/jna</url>
  <licenses>
    <license><name>LGPL-2.1-or-later</name></license>
    <license><name>Apache-2.0</name></license>
  </licenses>
</project>
EOF

%install
install -D -m 755 build/native/libjnidispatch.so %{buildroot}%{_libdir}/libjnidispatch.so
sysjar install --buildroot %{buildroot} \
	--artifact build/jna.pom:build/jna.jar \
	--file-name jna \
	--filelist .mfiles

%check
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java}"
"$JAVA_HOME/bin/jar" tf build/jna.jar > build/jar-list.txt
grep -qx 'com/sun/jna/Native.class' build/jar-list.txt
if grep -E '\.(so|dll|jnilib)$' build/jar-list.txt; then
	echo "jar contains a native library" >&2
	exit 1
fi
objdump -p %{buildroot}%{_libdir}/libjnidispatch.so > build/objdump.txt
grep -F 'SONAME' build/objdump.txt | grep -F 'libjnidispatch.so'
grep 'NEEDED' build/objdump.txt | grep 'libffi.so'
# No jna.nosys property: success means the default really is the system library.
"$JAVA_HOME/bin/java" --enable-native-access=ALL-UNNAMED \
	-cp build/jna.jar \
	-Djava.library.path=%{buildroot}%{_libdir} \
	com.sun.jna.Native > build/native-main.txt
cat build/native-main.txt
grep -F 'Native: 7.0.4 (5fb98531302accd485c534c452dd952a)' build/native-main.txt
grep -F 'Prefix: linux-' build/native-main.txt
grep -x 'Version: %{version}' build/native-main.txt

%files -f .mfiles
%license LICENSE AL2.0 LGPL2.1
%doc README.md CHANGES.md
%{_libdir}/libjnidispatch.so
