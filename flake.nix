{
  description = "Download qobuz music I already bought";

  inputs = {
    nixpkgs.url = "https://channels.nixos.org/nixpkgs-unstable/nixexprs.tar.zst";
  };

  outputs = inputs: {
    devShells = builtins.mapAttrs (system: pkgs: {
    default = pkgs.mkShell {
      packages = with pkgs; [
        python3
        uv
        prek
      ];
      env.UV_PROJECT_ENVIRONMENT = ".direnv/venv";
      shellHook = ''
      prek install
      if [! -d $UV_PROJECT_ENVIRONMENT ]
      then
        uv venv $UV_PROJECT_ENVIRONMENT --python ${pkgs.python3}/bin/python
      fi
      source $UV_PROJECT_ENVIRONMENT/bin/activate
      '';
    };
    }) inputs.nixpkgs.legacyPackages;
  };
}
