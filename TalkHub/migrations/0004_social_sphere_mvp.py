from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

def migrate_legacy_signups(apps, schema_editor):
    alias=schema_editor.connection.alias; LegacySignUp=apps.get_model("TalkHub","SignUp"); User=apps.get_model(settings.AUTH_USER_MODEL); Person=apps.get_model("TalkHub","Person")
    for old in LegacySignUp.objects.using(alias).all().iterator():
        email=(old.email or "").strip().lower()
        if not email or email=="nil": continue
        profile=Person.objects.using(alias).filter(email__iexact=email).first()
        if profile and profile.user_id: continue
        user=User.objects.using(alias).filter(email__iexact=email).first()
        if user is None:
            base=(old.username or f"legacy{old.pk}").strip()[:30] or f"legacy{old.pk}"; username=base; suffix=1
            while User.objects.using(alias).filter(username__iexact=username).exists():
                tail=f"_{suffix}"; username=f"{base[:150-len(tail)]}{tail}"; suffix+=1
            user=User.objects.using(alias).create(username=username,email=email,password=make_password(old.password or None),first_name=(old.username or "")[:30],is_active=True,date_joined=django.utils.timezone.now())
        if profile is None: Person.objects.using(alias).create(user_id=user.pk,first_name=(getattr(user,"first_name","") or old.username or "")[:30],last_name="",email=email,bio="")
        elif profile.user_id is None: profile.user_id=user.pk; profile.save(using=alias,update_fields=["user"])
    for user in User.objects.using(alias).all().iterator():
        if Person.objects.using(alias).filter(user_id=user.pk).exists(): continue
        email=(user.email or "").strip().lower() or f"legacy-{user.pk}@example.invalid"
        if Person.objects.using(alias).filter(email__iexact=email).exists(): email=f"legacy-{user.pk}@example.invalid"
        Person.objects.using(alias).create(user_id=user.pk,first_name=(getattr(user,"first_name","") or user.username or "User")[:30],last_name=(getattr(user,"last_name","") or "")[:30],email=email,bio="")

def noop_reverse(apps,schema_editor): pass
class Migration(migrations.Migration):
    dependencies=[("TalkHub","0003_signup"),migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations=[migrations.AddField(model_name="person",name="user",field=models.OneToOneField(blank=True,null=True,on_delete=django.db.models.deletion.CASCADE,related_name="social_profile",to=settings.AUTH_USER_MODEL)),migrations.AddField(model_name="person",name="bio",field=models.CharField(blank=True,default="",max_length=300)),migrations.AddField(model_name="post",name="content",field=models.TextField(blank=True,default="")),migrations.AddField(model_name="post",name="image_url",field=models.URLField(blank=True,default="",max_length=500)),migrations.AddField(model_name="post",name="video_url",field=models.URLField(blank=True,default="",max_length=500)),migrations.AddField(model_name="post",name="created_at",field=models.DateTimeField(auto_now_add=True,default=django.utils.timezone.now),preserve_default=False),migrations.CreateModel(name="Follow",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("created_at",models.DateTimeField(auto_now_add=True)),("follower",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="following_links",to="TalkHub.person")),("following",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="follower_links",to="TalkHub.person"))],options={"ordering":["-created_at","-id"],"constraints":[models.UniqueConstraint(fields=("follower","following"),name="unique_social_follow_pair")]}),migrations.AlterModelOptions(name="post",options={"ordering":["-created_at","-id"]}),migrations.AlterModelOptions(name="comment",options={"ordering":["created_at","id"]}),migrations.AlterModelOptions(name="like",options={"ordering":["-created_at","-id"]}),migrations.AlterModelOptions(name="save",options={"ordering":["-created_at","-id"]}),migrations.RunPython(migrate_legacy_signups,reverse_code=noop_reverse),migrations.DeleteModel(name="SignUp")]
