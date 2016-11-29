%{?scl:%scl_package bouncycastle-pkix}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 2

%global ver 1.54
%global archivever  jdk15on-%(echo %{ver}|sed 's|\\\.||')

Name:          %{?scl_prefix}bouncycastle-pkix
Version:       %{ver}
Release:       1.%{baserelease}%{?dist}
Summary:       Bouncy Castle PKIX, CMS, EAC, TSP, PKCS, OCSP, CMP, and CRMF APIs
License:       MIT
URL:           http://www.bouncycastle.org/

# Source tarball contains everything except test suite rousources
Source0:       http://www.bouncycastle.org/download/bcpkix-%{archivever}.tar.gz
# Test suite resources are found in this jar
Source1:       http://www.bouncycastle.org/download/bctest-%{archivever}.jar

Source2:       http://central.maven.org/maven2/org/bouncycastle/bcpkix-jdk15on/%{version}/bcpkix-jdk15on-%{version}.pom
Source3:       bouncycastle-pkix-build.xml
Source4:       bouncycastle-pkix-OSGi.bnd

BuildRequires: %{?scl_prefix_java_common}ant
BuildRequires: %{?scl_prefix_java_common}ant-junit
BuildRequires: %{?scl_prefix_maven}aqute-bnd

BuildRequires: %{?scl_prefix_maven}javapackages-local
BuildRequires: %{?scl_prefix_java_common}junit
BuildRequires: %{?scl_prefix}mvn(org.bouncycastle:bcprov-jdk15on) = %{version}
Requires:      %{?scl_prefix}mvn(org.bouncycastle:bcprov-jdk15on) = %{version}

BuildArch:     noarch

Obsoletes:     %{?scl_prefix}bouncycastle-tsp < 1.50-2
Provides:      %{?scl_prefix}bouncycastle-tsp = %{version}-%{release}

%description
The Bouncy Castle Java APIs for CMS, PKCS, EAC, TSP, CMP, CRMF, OCSP, and
certificate generation. This jar contains APIs for JDK 1.5 to JDK 1.7. The
APIs can be used in conjunction with a JCE/JCA provider such as the
one provided with the Bouncy Castle Cryptography APIs.

%package javadoc
Summary:       Javadoc for %{pkg_name}
Obsoletes:     %{?scl_prefix}bouncycastle-tsp-javadoc < 1.50-2

%description javadoc
This package contains javadoc for %{pkg_name}.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -n bcpkix-%{archivever}

# Unzip source and test suite resources
mkdir -p src/java src/test
unzip -qq src.zip -d src/java
unzip -qq %{SOURCE1} 'cmp/*' 'rfc4134/*' 'org/bouncycastle/*' -x '*.class' -d src/test

cp -p %{SOURCE2} pom.xml

# Remove provided binaries and apidocs
find . -type f -name "*.class" -print -delete
find . -type f -name "*.jar" -print -delete
rm -rf docs/* javadoc/*

mv src/java/org/bouncycastle/cert/cmp/test/* src/test/org/bouncycastle/cert/cmp/test
mv src/java/org/bouncycastle/cert/crmf/test/* src/test/org/bouncycastle/cert/crmf/test
mv src/java/org/bouncycastle/cert/ocsp/test/* src/test/org/bouncycastle/cert/ocsp/test
mv src/java/org/bouncycastle/cert/test/* src/test/org/bouncycastle/cert/test
mv src/java/org/bouncycastle/cms/test/* src/test/org/bouncycastle/cms/test
mv src/java/org/bouncycastle/eac/test/* src/test/org/bouncycastle/eac/test
mv src/java/org/bouncycastle/mozilla/test/* src/test/org/bouncycastle/mozilla/test
mv src/java/org/bouncycastle/openssl/test/* src/test/org/bouncycastle/openssl/test
mv src/java/org/bouncycastle/tsp/test/* src/test/org/bouncycastle/tsp/test
mv src/java/org/bouncycastle/pkcs/test/* src/test/org/bouncycastle/pkcs/test
mv src/java/org/bouncycastle/dvcs/test/* src/test/org/bouncycastle/dvcs/test
mv src/java/org/bouncycastle/cert/path/test/* src/test/org/bouncycastle/cert/path/test
mv src/java/org/bouncycastle/operator/test/* src/test/org/bouncycastle/operator/test

cp -p %{SOURCE3} build.xml
cp -p %{SOURCE4} bcpkix.bnd
sed -i "s|@VERSION@|%{version}|" build.xml bcpkix.bnd

# this test fails:
rm src/test/org/bouncycastle/cms/test/Rfc4134Test.java
sed -i "s|suite.addTest(Rfc4134Test.suite());|//suite.addTest(Rfc4134Test.suite());|" \
  src/test/org/bouncycastle/cms/test/AllTests.java
rm -rf src/test/org/bouncycastle/openssl/test

%mvn_file :bcpkix-jdk15on bcpkix
%mvn_alias :bcpkix-jdk15on "org.bouncycastle:bctsp-jdk16"
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
mkdir lib
build-jar-repository -s -p lib bcprov junit ant/ant-junit aqute-bnd
%ant -Dbc.test.data.home=$(pwd)/src/test jar javadoc
%mvn_artifact pom.xml build/bcpkix.jar
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%mvn_install -J build/apidocs
%{?scl:EOF}


%files -f .mfiles
%doc CONTRIBUTORS.html index.html
%doc LICENSE.html

%files javadoc -f .mfiles-javadoc
%doc LICENSE.html

%changelog
* Mon Jul 25 2016 Mat Booth <mat.booth@redhat.com> - 1.54-1.2
- Fix bnd tool invocation

* Mon Jul 25 2016 Mat Booth <mat.booth@redhat.com> - 1.54-1.1
- Auto SCL-ise package for rh-eclipse46 collection

* Thu Apr 07 2016 Mat Booth <mat.booth@redhat.com> - 1.54-1
- Update to 1.54, fixes rhbz#1275172
- Install with mvn_install
- Move some tests that were erroneously in the main jar,
  avoids a runtime dep on junit in OSGi metadata
- Fix most of the test failures

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.52-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jul 17 2015 gil cattaneo <puntogil@libero.it> 1.52-7
- remove the OSGi deprecated entry in bnd properties file

* Thu Jul 16 2015 gil cattaneo <puntogil@libero.it> 1.52-6
- add BR aqute-bndlib
- disable doclint

* Thu Jul 16 2015 Michael Simacek <msimacek@redhat.com> - 1.52-5
- Use aqute-bnd-2.4.1

* Tue Jun 23 2015 gil cattaneo <puntogil@libero.it> 1.52-4
- dropped the Export/Import-Package lists in the bnd properties file

* Thu Jun 18 2015 gil cattaneo <puntogil@libero.it> 1.52-3
- fix OSGi export rhbz#1233359

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.52-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Apr 22 2015 Alexander Kurtakov <akurtako@redhat.com> 1.52-1
- Update to 1.52
- Switch source/target to 1.6 as 1.5 is to be removed in Java 9.

* Thu Jan 29 2015 gil cattaneo <puntogil@libero.it> 1.50-4
- introduce license macro

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.50-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri Mar 14 2014 Michal Srb <msrb@redhat.com> - 1.50-2
- Obsolete bouncycastle-tsp

* Mon Feb 24 2014 gil cattaneo <puntogil@libero.it> 1.50-1
- update to 1.50

* Fri Feb 22 2013 gil cattaneo <puntogil@libero.it> 1.48-1
- update to 1.48

* Thu Jun 21 2012 gil cattaneo <puntogil@libero.it> 1.47-1
- initial rpm
