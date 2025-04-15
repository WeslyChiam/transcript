{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.ffmpeg  # Install ffmpeg
    pkgs.python38
    pkgs.python38Packages.pip  # Ensure pip is available
  ];

  shellHook = ''
    # Custom shell commands can go here, if necessary
  '';
}
