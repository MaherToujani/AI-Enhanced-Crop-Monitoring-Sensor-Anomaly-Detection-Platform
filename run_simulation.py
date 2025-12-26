import argparse
import sys
import requests
from simulator.sensor_simulator import SimulatorConfig, run_simulation


def get_jwt_token(api_base_url: str, username: str = "admin", password: str = "admin") -> str:
    """Login and get JWT access token."""
    login_url = f"{api_base_url.rstrip('/')}/api/auth/login/"
    
    try:
        response = requests.post(
            login_url,
            json={"username": username, "password": password},
            timeout=5
        )
        response.raise_for_status()
        return response.json()["access"]
    except requests.exceptions.RequestException:
        print(f"ERROR: Backend not running at {api_base_url}")
        print("Start Docker containers with: docker-start.bat")
        sys.exit(1)
    except KeyError:
        print(f"ERROR: Login failed. Check username/password.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Run sensor simulator")
    parser.add_argument("--api-base-url", default="http://localhost:8000")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin")
    parser.add_argument("--plots", default="1", help="Comma-separated plot IDs")
    parser.add_argument("--interval", type=int, default=10, help="Seconds between steps")
    parser.add_argument("--steps", type=int, default=30, help="Number of steps")
    parser.add_argument("--anomaly-ratio", type=float, default=0.4, help="Anomaly ratio (0.0-1.0, default: 0.4)")
    
    args = parser.parse_args()

    print("Getting JWT token...")
    access_token = get_jwt_token(args.api_base_url, args.username, args.password)
    print("Starting simulation...\n")

    config = SimulatorConfig(
        api_base_url=args.api_base_url,
        access_token=access_token,
        plot_ids=[int(p.strip()) for p in args.plots.split(",") if p.strip()],
        interval_seconds=args.interval,
        steps=args.steps,
        anomaly_ratio=args.anomaly_ratio,
    )

    run_simulation(config)
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()
