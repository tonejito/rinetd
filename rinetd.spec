# rinetd is built against libfoo and installed under /usr/local (to match the
# libfoo package and the bundled systemd unit). Skip the empty debuginfo
# subpackage since the autotools build does not compile with -g.
%global debug_package %{nil}

Name:           rinetd
Version:        0.74.2
Release:        1%{?dist}
Summary:        Internet TCP/UDP port redirection server

License:        GPLv2+
URL:            https://github.com/samhocevar/rinetd
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  systemd-rpm-macros
# rinetd links against libfoo (headers + library, installed in /usr/local)
BuildRequires:  libfoo
Requires:       libfoo

%description
rinetd redirects TCP and UDP connections from one IP address and port to
another. It is a single-process server that handles any number of connections
using the select() system call. This build is linked against libfoo and ships a
systemd unit that runs rinetd in the foreground under systemd supervision.

%prep
%setup -q

%build
# The dist tarball already ships configure/Makefile.in, but regenerate anyway so
# the build does not depend on the autotools version used to roll the tarball
./bootstrap
# Binary and config under /usr/local (matches libfoo and the unit); sysconfdir
# is also compiled into the binary as the default config file location
./configure --prefix=/usr/local --sysconfdir=/usr/local/etc
make %{?_smp_mflags}

%install
# Installs the binary to /usr/local/sbin and rinetd.conf to /usr/local/etc
make install DESTDIR=%{buildroot}
# Ship the systemd unit in /usr/local/lib/systemd/system, which is part of the
# default unit search path (the unit is only in EXTRA_DIST otherwise)
install -D -m 0644 etc/rinetd.service %{buildroot}/usr/local/lib/systemd/system/rinetd.service

%check
# src/rinetd.h silently falls back to "/etc" when -DSYSCONFDIR is missing, which
# would ship a daemon that ignores the rinetd.conf we install. --help prints the
# compiled-in default, so assert on it.
# %%check runs after %%install, so test the binary that actually gets packaged
# rather than a build-tree path.
# libfoo lives in /usr/local/lib, which is not on the default loader path.
LD_LIBRARY_PATH=/usr/local/lib %{buildroot}/usr/local/sbin/rinetd --help | grep -q '(default: /usr/local/etc/rinetd.conf)'

%post
%systemd_post rinetd.service

%preun
%systemd_preun rinetd.service

%postun
%systemd_postun_with_restart rinetd.service

%files
/usr/local/sbin/rinetd
%config(noreplace) /usr/local/etc/rinetd.conf
/usr/local/share/man/man8/rinetd.8*
# /usr/local/lib/systemd{,/system} are not owned by the filesystem package
%dir /usr/local/lib/systemd
%dir /usr/local/lib/systemd/system
/usr/local/lib/systemd/system/rinetd.service

%changelog
* Wed Sep 09 2026 Andrés Hernández <tonejito@comunidad.unam.mx> - 0.74.2-1
- Initial package; linked against libfoo, ships systemd unit
