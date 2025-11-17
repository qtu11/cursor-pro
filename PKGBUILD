# Maintainer: Canmi21 <9997200@qq.com>
# Contributor: Canmi (Canmi21)

pkgname=cursor-pro-git
pkgver=1.9.05
pkgrel=1
pkgdesc="Reset Cursor AI MachineID & Auto Sign Up / In & Bypass Higher Token Limit"
arch=('x86_64')
url="https://github.com/qtu11/cursor-pro"
license=('MIT' 'Attribution-NonCommercial-NoDerivatives 4.0 International')
depends=('python' 'cursor-bin')
makedepends=('git' 'python' 'pyinstaller' 'uv')
provides=('cursor-pro')
source=("cursor-pro::git+https://github.com/qtu11cursor-pro.git" "https://raw.githubusercontent.com/canmi21/openjlc/refs/heads/main/LICENSE")
sha256sums=('SKIP' 'SKIP')

pkgver() {
  cd "$srcdir/cursor-pro"
  git describe --tags --always | sed 's/^v//;s/-/./g'
}

build() {
  cd "$srcdir/cursor-pro"
  uv venv .venv
  source .venv/bin/activate
  uv pip install -r requirements.txt
  pyinstaller --clean --noconfirm --onefile main.py --name cursor-pro
}

package() {
  install -Dm644 "$srcdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/mit_license"
  install -Dm644 "$srcdir/cursor-pro/LICENSE.md" "$pkgdir/usr/share/licenses/$pkgname/attribution_non_commercial_no_derivatives_license"
  install -Dm755 "$srcdir/cursor-pro/dist/cursor-pro" "$pkgdir/usr/bin/cursor-pro"
}