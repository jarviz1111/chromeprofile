{pkgs}: {
  deps = [
    pkgs.postgresql
    pkgs.chromium
    pkgs.glib
    pkgs.geckodriver
  ];
}
