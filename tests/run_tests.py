"""
Script para ejecutar tests del Centro de Yoga Paz Interior
"""

import subprocess
import sys
import os

def run_tests():
    """Ejecutar todos los tests"""
    print("Ejecutando tests del Centro de Yoga Paz Interior...")
    
    os.environ["TESTING"] = "true"
    
    commands = [
        ["pytest", "tests/test_cache.py", "-v", "--cov=capb"],
        ["pytest", "tests/test_optimization.py", "-v", "--cov=routes"],
        ["pytest", "tests/", "-v", "--cov=.", "--cov-report=html"]
    ]
    
    for cmd in commands:
        print(f"\n Ejecutando: {' '.join(cmd)}")
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            print("Algunos tests fallaron")
            sys.exit(1)
    
    print("✅ Todos los tests pasaron exitosamente!")

if __name__ == "__main__":
    run_tests()