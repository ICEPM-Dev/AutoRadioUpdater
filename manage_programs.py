#!/usr/bin/env python3
"""
CLI tool to manage radio programs configuration
"""
import argparse
import sys
from src.config_manager import ConfigManager
from src.scraper_factory import ScraperFactory


def list_programs(config_manager):
    """List all configured programs"""
    programs = config_manager.get_all_programs()
    
    if not programs:
        print("No hay programas configurados.")
        return
    
    print("\nProgramas configurados:")
    print("-" * 80)
    for i, program in enumerate(programs, 1):
        status = "✓ Habilitado" if program.get("enabled", True) else "✗ Deshabilitado"
        print(f"{i}. {program['name']}")
        print(f"   URL: {program['url']}")
        print(f"   Estado: {status}")
        if program.get("description"):
            print(f"   Descripción: {program['description']}")
        print()


def add_program(config_manager, name, url, description=""):
    """Add a new program"""
    factory = ScraperFactory()
    
    if not factory.is_supported(url):
        print(f"Error: La URL {url} no es compatible con ningún scraper disponible.")
        print(f"Dominios soportados: {', '.join(factory.get_supported_domains())}")
        return False
    
    config_manager.add_program(name, url, description)
    print(f"Programa '{name}' agregado exitosamente.")
    return True


def remove_program(config_manager, name):
    """Remove a program"""
    programs = config_manager.get_all_programs()
    program_names = [p['name'] for p in programs]
    
    if name not in program_names:
        print(f"Error: No se encontró el programa '{name}'.")
        print(f"Programas disponibles: {', '.join(program_names)}")
        return False
    
    config_manager.remove_program(name)
    print(f"Programa '{name}' eliminado exitosamente.")
    return True


def enable_program(config_manager, name):
    """Enable a program"""
    config_manager.enable_program(name)
    print(f"Programa '{name}' habilitado.")


def disable_program(config_manager, name):
    """Disable a program"""
    config_manager.disable_program(name)
    print(f"Programa '{name}' deshabilitado.")


def show_supported_domains():
    """Show supported domains"""
    factory = ScraperFactory()
    domains = factory.get_supported_domains()
    
    print("\nDominios soportados:")
    print("-" * 40)
    for domain in sorted(domains):
        print(f"  • {domain}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Gestionar programas de radio")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # List command
    subparsers.add_parser('list', help='Listar todos los programas')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Agregar un nuevo programa')
    add_parser.add_argument('name', help='Nombre del programa')
    add_parser.add_argument('url', help='URL del programa')
    add_parser.add_argument('--description', '-d', default='', help='Descripción del programa')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Eliminar un programa')
    remove_parser.add_argument('name', help='Nombre del programa a eliminar')
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Habilitar un programa')
    enable_parser.add_argument('name', help='Nombre del programa a habilitar')
    
    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Deshabilitar un programa')
    disable_parser.add_argument('name', help='Nombre del programa a deshabilitar')
    
    # Supported domains command
    subparsers.add_parser('domains', help='Mostrar dominios soportados')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config_manager = ConfigManager()
    
    if args.command == 'list':
        list_programs(config_manager)
    elif args.command == 'add':
        add_program(config_manager, args.name, args.url, args.description)
    elif args.command == 'remove':
        remove_program(config_manager, args.name)
    elif args.command == 'enable':
        enable_program(config_manager, args.name)
    elif args.command == 'disable':
        disable_program(config_manager, args.name)
    elif args.command == 'domains':
        show_supported_domains()


if __name__ == '__main__':
    main()
