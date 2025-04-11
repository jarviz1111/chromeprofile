{pkgs}: {
  deps = [
    pkgs.zip
    pkgs.postgresql
    pkgs.chromium
    pkgs.glib
    pkgs.geckodriver
  ];
}
