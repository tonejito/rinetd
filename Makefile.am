
AUTOMAKE_OPTIONS = foreign dist-bzip2

SUBDIRS = src

EXTRA_DIST = bootstrap COPYING CHANGES.md README.md index.html rinetd.vcxproj \
	etc/rinetd.service $(SPEC) \
	$(man_MANS) $(sysconf_DATA)

man_MANS = rinetd.8
# Installed as $(sysconfdir)/rinetd.conf — automake strips the directory part.
sysconf_DATA = etc/rinetd.conf
noinst_DATA = index.html

# If roffit is available, regenerate index.html
index.html: rinetd.8
	if which roffit >/dev/null 2>&1; then roffit < $^ > $@; else touch $@; fi

# This is for Travis CI; we don’t have a testsuite yet.
test:
	true

################################################################################
# RPM packaging.
#
# Builds a binary RPM and an SRPM from a “make dist” tarball, so the package
# only ever contains files automake knows about.
#
# rinetd links against libfoo, so the libfoo RPM must be built and installed
# first:
#     make -C ../libfoo rpm && sudo dnf install ~/rpmbuild/RPMS/*/libfoo-*.rpm

SPEC = rinetd.spec
RPM_TOPDIR = $(HOME)/rpmbuild

# automake writes “make dist” tarballs into the build root; collect them here
# instead. distdir cannot simply be pointed at pkg/, because $(am__tar) archives
# the directory by path and the prefix would end up inside the tarball.
PKGDIR = $(top_builddir)/pkg

.PHONY: pkg rpm srpm spec-check

# Roll both tarballs into pkg/. Depend on “dist”, not on dist-gzip and
# dist-bzip2 separately: each of those deletes $(distdir) when it finishes, so
# the second one would find nothing to archive. “dist” builds every format in
# $(DIST_TARGETS) (bzip2 and gzip here, via AUTOMAKE_OPTIONS) with the cleanup
# suppressed until all of them are done.
pkg: dist
	$(MKDIR_P) $(PKGDIR)
	mv -f $(distdir).tar.gz $(distdir).tar.bz2 $(PKGDIR)/

# “make clean” does not know about pkg/; drop it along with the build tree.
distclean-local:
	-rm -rf $(PKGDIR)

# Source0/%setup only find the tarball if the spec version matches AC_INIT.
spec-check:
	@v=`rpmspec -q --srpm --qf '%{version}' $(srcdir)/$(SPEC)`; \
	if test "$$v" != "$(VERSION)"; then \
	  echo "$(SPEC): Version $$v does not match configure.ac $(VERSION)" >&2; \
	  exit 1; \
	fi

# Stage the tarball and the spec where rpmbuild expects them.
$(RPM_TOPDIR)/SOURCES/$(distdir).tar.gz: pkg
	$(MKDIR_P) $(RPM_TOPDIR)/BUILD $(RPM_TOPDIR)/BUILDROOT $(RPM_TOPDIR)/RPMS \
	           $(RPM_TOPDIR)/SRPMS $(RPM_TOPDIR)/SOURCES $(RPM_TOPDIR)/SPECS
	cp $(PKGDIR)/$(distdir).tar.gz $(RPM_TOPDIR)/SOURCES/
	cp $(srcdir)/$(SPEC) $(RPM_TOPDIR)/SPECS/

rpm: spec-check $(RPM_TOPDIR)/SOURCES/$(distdir).tar.gz
	rpmbuild -ba $(RPM_TOPDIR)/SPECS/$(SPEC)

srpm: spec-check $(RPM_TOPDIR)/SOURCES/$(distdir).tar.gz
	rpmbuild -bs $(RPM_TOPDIR)/SPECS/$(SPEC)
