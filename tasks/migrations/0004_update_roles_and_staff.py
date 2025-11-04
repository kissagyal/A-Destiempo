from django.db import migrations


def map_roles_and_staff(apps, schema_editor):
	PerfilUsuario = apps.get_model('tasks', 'PerfilUsuario')
	User = apps.get_model('auth', 'User')
	# Mapear valores antiguos a nuevos
	for perfil in PerfilUsuario.objects.all():
		old = perfil.tipo_usuario
		if old == 'usuario':
			perfil.tipo_usuario = 'cliente'
			perfil.save(update_fields=['tipo_usuario'])
		elif old == 'empleado':
			perfil.tipo_usuario = 'vendedor'
			perfil.save(update_fields=['tipo_usuario'])
			# Asegurar acceso a admin si corresponde
			try:
				user = User.objects.get(pk=perfil.user_id)
				if not user.is_staff:
					user.is_staff = True
					user.save(update_fields=['is_staff'])
			except User.DoesNotExist:
				pass


def reverse_map_roles_and_staff(apps, schema_editor):
	PerfilUsuario = apps.get_model('tasks', 'PerfilUsuario')
	User = apps.get_model('auth', 'User')
	for perfil in PerfilUsuario.objects.all():
		new = perfil.tipo_usuario
		if new == 'cliente':
			perfil.tipo_usuario = 'usuario'
			perfil.save(update_fields=['tipo_usuario'])
		elif new == 'vendedor':
			perfil.tipo_usuario = 'empleado'
			perfil.save(update_fields=['tipo_usuario'])
			# no forzamos revertir is_staff para no perder ajustes manuales


class Migration(migrations.Migration):

	dependencies = [
		('tasks', '0003_remove_inventario_unique_disco_sucursal_and_more'),
	]

	operations = [
		migrations.RunPython(map_roles_and_staff, reverse_map_roles_and_staff),
	]
