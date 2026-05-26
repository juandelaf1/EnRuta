#!/usr/bin/env python
"""EnRuta — Punto de entrada."""
import sys
sys.path.insert(0, ".")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="EnRuta — Logística Colaborativa Rural")
    parser.add_argument("command", nargs="?", default="dashboard",
                        choices=["pipeline", "match", "dashboard", "all"],
                        help="Comando a ejecutar")
    args = parser.parse_args()

    if args.command in ("pipeline", "all"):
        from src.pipeline import run_pipeline
        run_pipeline()

    if args.command in ("match", "all"):
        from src.matching.engine import match_all
        df = match_all(top_k=500)
        if not df.empty:
            print(f"Matches: {len(df)} | Mejor score: {df.iloc[0]['score']}")

    if args.command in ("dashboard", "all"):
        from src.dashboard import app
        print("[EnRuta] Dashboard en http://127.0.0.1:8050")
        app.run(debug=True, port=8050)
