"""Quick check that the app imports and every route answers."""
import app as A

def main():
    c = A.app.test_client()
    checks = ["/", "/about", "/contact", "/search?q=test"]
    ok = True
    for path in checks:
        code = c.get(path).status_code
        print(f"  {path:24} -> {code}")
        ok = ok and code < 500
    print("PREFLIGHT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
