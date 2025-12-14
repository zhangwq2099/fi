"""
启动微服务的便捷脚本
"""
import uvicorn
import sys

if __name__ == "__main__":
    print("=" * 50)
    print("Starting Fund Trading Microservice")
    print("=" * 50)
    print("Service will be available at:")
    print("  - API: http://localhost:8000")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the service\n")
    
    try:
        uvicorn.run(
            "main_v2:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\nService stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError starting service: {e}")
        sys.exit(1)

