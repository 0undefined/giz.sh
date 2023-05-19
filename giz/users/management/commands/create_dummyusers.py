
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password

from users.models import Invitation

User = get_user_model()

class Command(BaseCommand):
    help = "Create dummy users"

    def add_arguments(self, parser):
        parser.add_argument("-n", "--num", type=int)

    def handle(self, *args, **options):
        try:
            superuser = User.objects.filter(is_superuser=True).first()
        except:
            raise CommandError("You need to create a superuser first!")

        num = 1
        if options['num']:
            num = options['num']

        if num < 1:
            raise CommandError("You need give a positive integer!")

        usernames = [
            'rosemary_stout', 'callahan_taylor', 'sofia_ahmed', 'harry_stuart', 'stormi_meza', 'lucian_gross', 'angel_grimes', 'harlan_nash', 'novah_andersen', 'alistair_wong', 'adelaide_choi',
            'khari_patel', 'madeline_morse', 'bode_burke', 'vera_miranda', 'rory_valencia', 'maddison_day', 'kayson_ortiz', 'anna_stephenson', 'joe_thompson', 'madison_shelton', 'leonel_phelps',
            'laney_michael', 'bronson_garcia', 'amelia_beltran', 'ricky_jimenez', 'adeline_grant', 'leon_stephenson', 'khaleesi_wyatt', 'sam_robertson', 'harmony_adams', 'hudson_hunter', 'khloe_ward',
            'jameson_bradshaw', 'berkley_elliott', 'blake_reese', 'rosemary_brewer', 'cruz_curry', 'alison_lawson', 'lane_pace', 'giana_simpson', 'elliott_yoder', 'emerie_cooper', 'jonathan_good',
            'nathalia_garrett', 'kairo_stokes', 'miranda_fitzgerald', 'peyton_patton', 'lorelei_sexton', 'mylo_merritt', 'kaisley_moody', 'ryland_calhoun', 'thalia_collier', 'edison_guzman',
            'ashley_duncan', 'avery_caldwell', 'evelynn_chan', 'frank_ryan', 'morgan_villegas', 'clyde_corona', 'marianna_gonzales', 'brayden_dean', 'julianna_duncan', 'avery_strong', 'margo_henson',
            'bellamy_lozano', 'cecelia_santiago', 'beckham_medina', 'elliana_dunn', 'dawson_shannon', 'harlee_mitchell', 'jaxon_walsh', 'leia_baxter', 'tomas_woodard', 'aubrie_benson',
            'desmond_strickland', 'nia_bryant', 'jonah_ochoa', 'luciana_joseph', 'kyle_noble', 'hunter_combs', 'ahmad_wilcox', 'ashlyn_mcmahon', 'jakob_gibson', 'eden_bryant', 'jonah_garrison',
            'cadence_marquez', 'malakai_burke', 'vera_nelson', 'dylan_ahmed', 'jolie_strong', 'axl_cabrera', 'daleyza_villa', 'clay_bass', 'zahra_o’connor', 'princeton_durham', 'tiffany_steele',
            'elian_robles', 'felicity_levy', 'harold_shepard', 'noor_arias', 'alec_nielsen', 'vienna_ahmed', 'harry_zhang', 'sarai_neal', 'kane_barrera', 'beatrice_robles', 'otto_ramos',
            'alice_benjamin', 'kyro_aguirre', 'ariah_bonilla', 'aden_reynolds', 'isabelle_miranda', 'rory_blake', 'amanda_sanford', 'truett_watts', 'melissa_maddox', 'lyric_best', 'lexie_rush',
            'kaiser_kline', 'sevyn_walters', 'colson_huber', 'raquel_erickson', 'johnny_mccann', 'joyce_huerta', 'douglas_yang', 'angelina_best', 'harlem_andersen', 'zoie_garza', 'judah_mccann',
            'joyce_shaffer', 'dexter_perez', 'eleanor_weiss', 'koa_powell', 'vivian_morris', 'christian_correa', 'valery_adams', 'hudson_burch', 'freyja_tapia', 'samir_combs', 'irene_richard',
            'ahmed_mcclure', 'estella_randall', 'trenton_duke', 'melani_calhoun', 'gary_donaldson', 'natasha_frazier', 'callum_clay', 'aliana_buck', 'jon_solis', 'miracle_douglas', 'derek_mcgee',
            'kayleigh_simon', 'zayne_stone', 'catalina_jacobson', 'legacy_good', 'nathalia_atkins', 'cason_sellers', 'mercy_rubio', 'titan_swanson', 'helen_oliver', 'karson_cobb', 'aviana_sawyer',
            'jefferson_richard', 'davina_moss', 'porter_decker', 'aleena_chapman', 'knox_ingram', 'katie_lee', 'jack_huff', 'karsyn_wallace', 'chase_pittman', 'marie_trujillo', 'apollo_hoffman',
            'aspen_bridges', 'mohammed_chang', 'ophelia_schaefer', 'ishaan_flowers', 'ariya_horne', 'zev_lawrence', 'lauren_salgado', 'trace_mora', 'jemma_farrell', 'ty_schmitt', 'queen_vega']

        User.objects.bulk_create([
            User(
                username=username,
                password=make_password('asdasdasd'),
                is_active=True,
                is_superuser=False,
                repo_size_limit=0,
            ) for username in usernames[:num]
        ])
