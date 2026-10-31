# Publicar en GitHub

El proyecto está preparado como repositorio Git. Para publicarlo en tu cuenta:

1. En GitHub, crea un repositorio público vacío llamado `NEO-LYRICS-ULTIMATE` (sin README, licencia ni `.gitignore`, porque ya están incluidos aquí).
2. Extrae este ZIP y abre una terminal en la carpeta `NEO-LYRICS-ULTIMATE`.
3. Ejecuta:

```bash
git init
git add .
git commit -m "Initial cross-platform release 1.2.0"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/NEO-LYRICS-ULTIMATE.git
git push -u origin main
```

Reemplaza `TU_USUARIO` por tu usuario real de GitHub. GitHub puede pedir autenticación mediante navegador o token; nunca pegues un token en un chat ni lo guardes en el repositorio.

Al subir `main`, GitHub Actions ejecutará la matriz de pruebas Ubuntu/Windows. Para publicar un release, crea y sube un tag:

```bash
git tag v1.2.0
git push origin v1.2.0
```

El workflow de release compilará el paquete Python y creará el Release asociado al tag.
