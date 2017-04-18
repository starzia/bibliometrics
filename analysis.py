import pprint
import unittest
import statistics
import string

import editdistance

# these two lines are necessary to use matplotlib in pycharm on a mac (http://stackoverflow.com/a/21789908)
import matplotlib as mpl
mpl.use('TkAgg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker

from professor import Professor
from typing import List, Dict, AnyStr, Tuple
from professor_scraper import load_paper_list
from google_scholar import Paper, STARTING_YEAR, get_year
from google_sheets import GoogleSheets
from web_util import strip_whitespace

AFFILIATIONS = ['Northwestern', 'Harvard', 'Chicago', 'MIT', 'Stanford', 'UPenn', 'Berkeley', 'Yale', 'Columbia', 'Dartmouth']

ABBREVIATIONS = {
    'the': None,
    'of': None,
    'and': '&',
    'journal': 'j',
    'review': 'rev',
    'research': 'res',
    'studies': 'stud',
    'science': 'sci',
    'psychological': 'psych',
    'psychology': 'psych',
    'american': 'amer',
    'sociological': 'soc',
    'quarterly': 'q',
    'management': 'mgmt',
    'proceedings': 'proc',
    'national': 'natl',
    'academy': 'ac',
    'organization': 'org',
    'organizational': 'org',
    'affairs': 'aff'
}

TOP_JOURNALS = [
    'accounting review',
    'journal of accounting research',
    'journal of accounting and economics',

    'american economic review',
    'quarterly journal of economics',
    'journal of political economy',
    'econometrica',
    # 2nd tier economics:
    'journal of economic theory',
    'review of economic studies',
    'rand journal of economics',
    'american economic journal: microeconomics',
    'american economic journal: macroeconomics',
    'journal of monetary economics',

    'journal of finance',
    'review of financial studies',
    'journal of financial economics',

    'journal of consumer research',
    'journal of marketing research',
    'marketing science',

    'management science',
    'operations research',
    'manufacturing and service operations management',

    'psychological science',
    'journal of personality and social psychology',
    'organizational behavior and human decision processes',

    'american sociological review',
    'american journal of sociology',
    'sociological science',

    'administrative science quarterly',
    'organization science',
    'academy of management journal',

    'proceedings of the national academy of sciences',

    'science',
    'nature',
]

HIGH_COLLISION_TOP_JOURNALS = [
    'science',
    'nature',
]

KELLOGG_DEPTS = {
    'Accounting': ['northwestern_daniel_aobdia',
                   'northwestern_craig_chapman',
                   'northwestern_ronald_a_dye',
                   'northwestern_matthew_lyle',
                   'northwestern_robert_magee',
                   'northwestern_james_naughton',
                   'northwestern_swaminathan_sridharan',
                   'northwestern_linda_vincent',
                   'northwestern_beverly_walther',
                   'northwestern_clare_wang',
                   'northwestern_danqi_hu'],
    'Finance': ['northwestern_torben_andersen',
                'northwestern_scott_baker',
                'northwestern_efraim_benmelech',
                'northwestern_nicolas_crouzet',
                'northwestern_anthony_defusco',
                'northwestern_ian_dewbecker',
                'northwestern_janice_c_eberly',
                'northwestern_michael_j_fishman',
                'northwestern_carola_frydman',
                'northwestern_benjamin_iverson',
                'northwestern_ravi_jagannathan',
                'northwestern_robert_korajczyk',
                'northwestern_lorenz_kueng',
                'northwestern_david_a_matsa',
                'northwestern_robert_l_mcdonald',
                'northwestern_brian_melzer',
                'northwestern_konstantin_w_milbradt',
                'northwestern_john_mondragon',
                'northwestern_charles_nathanson',
                'northwestern_aharon_ofer',
                'northwestern_dimitris_papanikolaou',
                'northwestern_mitchell_a_petersen',
                'northwestern_artur_raviv',
                'northwestern_constantinos_skiadas',
                'northwestern_viktor_todorov',
                'northwestern_kathleen_hagerty',
                'northwestern_filippo_mezzanotti',
                'northwestern_sergio_rebelo',
                'northwestern_paola_sapienza'],
    'Marketing': ['northwestern_eric_t_anderson',
                  'northwestern_james_anderson',
                  'northwestern_ulf_bockenholt',
                  'northwestern_miguel_brendl',
                  'northwestern_bobby_calder',
                  'northwestern_gregory_carpenter',
                  'northwestern_moran_cerf',
                  'northwestern_alexander_chernev',
                  'northwestern_jennifer_cutler',
                  'northwestern_kelly_goldsmith',
                  'northwestern_brett_gordon',
                  'northwestern_kent_grayson',
                  'northwestern_lakshman_krishnamurthi',
                  'northwestern_aparna_labroo',
                  'northwestern_angela_y_lee',
                  'northwestern_blake_mcshane',
                  'northwestern_neal_roese',
                  'northwestern_derek_d_rucker',
                  'northwestern_rima_touretillery',
                  'northwestern_alice_tybout',
                  'northwestern_song_yao',
                  'northwestern_florian_zettelmeyer',
                  'northwestern_anne_coughlan',
                  'northwestern_philip_kotler',
                  'northwestern_brian_sternthal',
                  'northwestern_anna_tuchman'],
    'MEDS': ['northwestern_nabil_alnajjar',
             'northwestern_sandeep_baliga',
             'northwestern_achal_bassamboo',
             'northwestern_erika_deserranno',
             'northwestern_georgy_egorov',
             'northwestern_timothy_feddersen',
             'northwestern_ronen_gradwohl',
             'northwestern_taiwei_hu',
             'northwestern_willemien_kets',
             'northwestern_peter_klibanoff',
             'northwestern_daniel_martin',
             'northwestern_dylan_minor',
             'northwestern_ameet_morjaria',
             'northwestern_nicola_persico',
             'northwestern_nancy_qian',
             'northwestern_yuval_salant',
             'northwestern_alvaro_sandroni',
             'northwestern_james_schummer',
             'northwestern_eran_shmaya',
             'northwestern_jorg_spenkuch',
             'northwestern_jan_a_van_mieghem',
             'northwestern_nemanja_antic',
             'northwestern_david_austensmith',
             'northwestern_joshua_mollner'],
    'MORS': ['northwestern_jeanne_brett',
             'northwestern_maryam_kouchaki',
             'northwestern_nour_kteily',
             'northwestern_jon_maner',
             'northwestern_victoria_medvec',
             'northwestern_loran_nordgren',
             'northwestern_william_ocasio',
             'northwestern_lauren_rivera',
             'northwestern_edward_ned_smith',
             'northwestern_nicole_stephens',
             'northwestern_leigh_thompson',
             'northwestern_brian_uzzi',
             'northwestern_dashun_wang',
             'northwestern_adam_waytz',
             'northwestern_klaus_weber',
             'northwestern_edward_zajac',
             'northwestern_sally_blount',
             'northwestern_jillian_chown',
             'northwestern_brayden_king'],
    'Operations': ['northwestern_chaithanya_bandi',
                   'northwestern_robert_bray',
                   'northwestern_sunil_chopra',
                   'northwestern_itai_gurvich',
                   'northwestern_ozge_islegen',
                   'northwestern_martin_lariviere',
                   'northwestern_antonio_morenogarcia',
                   'northwestern_daniel_russo'],
    'Strategy': ['northwestern_daniel_barron',
                 'northwestern_david_besanko',
                 'northwestern_nicola_bianchi',
                 'northwestern_meghan_busse',
                 'northwestern_david_dranove',
                 'northwestern_craig_garthwaite',
                 'northwestern_george_georgiadis',
                 'northwestern_paul_hirsch',
                 'northwestern_thomas_n_hubbard',
                 'northwestern_edward_fx_hughes',
                 'northwestern_benjamin_f_jones',
                 'northwestern_jin_li',
                 'northwestern_niko_matouschek',
                 'northwestern_michael_mazzeo',
                 'northwestern_michael_powell',
                 'northwestern_mark_satterthwaite',
                 'northwestern_daniel_spulber',
                 'northwestern_amanda_starc',
                 'northwestern_jeroen_swinkels',
                 'northwestern_benjamin_friedrich',
                 'northwestern_therese_mcguire',
                 'northwestern_sara_moreira',
                 'northwestern_elena_prager',
                 'northwestern_bryony_reich']
}

pp = pprint.PrettyPrinter(indent=4)
non_letter_remover = str.maketrans('', '', string.punctuation + string.digits)

# global plotting parameters
plt.rcParams["font.serif"] = "Times New Roman"
plt.rcParams["font.family"] = "serif"
plt.rcParams['figure.figsize'] = 4, 4  # figure size in inches


def abbreviate(journal_name):
    output = []
    for tok in norm_str(journal_name).split(' '):
        if tok in ABBREVIATIONS:
            if ABBREVIATIONS[tok]:
                output.append(ABBREVIATIONS[tok])
        else:
            output.append(tok)
    return norm_str(' '.join(output))


def is_a_top_journal(contains_journal_name):
    for j in TOP_JOURNALS:
        if is_in_journal(contains_journal_name, j):
            return True
    return False


def is_in_journal(contains_journal_name, journal):
    abbreviated_name = abbreviate(contains_journal_name)
    if journal in HIGH_COLLISION_TOP_JOURNALS:
        return abbreviate(journal) == abbreviated_name
    else:
        return abbreviate(journal) in abbreviated_name


# These variables control which papers are considered.
starting_year = STARTING_YEAR
ignored_scholar_citation_ids = set([])
try:
    with open('papers_to_ignore.txt', 'r') as f:
        ignored_scholar_citation_ids = set([l.replace('\n', '') for l in f.readlines()])
except FileNotFoundError:
    print("WARNING: did not find papers_to_ignore.txt")


def load_scholar_papers(prof, ignore_search_results=False):
    global starting_year, scholar_paper_cache
    papers = []
    for f in ['scholar_profile', 'scholar_search']:
        papers.extend([p for p in [Paper.from_string(s) for s in load_paper_list(f, prof)]
                       if p.year > starting_year and p.id not in ignored_scholar_citation_ids])
        # ignore Scholar search results if we have a profile
        if len(papers) > 0 or ignore_search_results:
            break
    return papers


def citations(paper_list: List[Paper]) -> List[Tuple[str, str]]:
    return [(paper.venue, paper.pretty_citation()) for paper in paper_list]


def count_citations(prof):
    return sum(int(paper.scholar_citations) for paper in load_scholar_papers(prof))


def citation_aging_report(profs) -> List[List[int]]:
    """:return: the number of citations for professors of "age" 0 through 10 years.  Anyone older than 10 is considered
     10 because we ignore papers older than ten years anyway."""
    return [[count_citations(p) for p in profs if p.graduation_year and
             (2018 - int(p.graduation_year) == i if i < 11 else 2018 - int(p.graduation_year) >= i)]
            for i in range(1, 12)]


def prestigious_rate_aging_report(profs) -> List[List[float]]:
    """:return: the career-average rate of publication in prestigious journals
       for professors of "age" 0 through 10 years.
       Anyone older than 10 is considered 10 because we ignore papers older than ten years anyway."""
    top_papers = papers_in_top_journals(profs)
    return [[float(len(top_papers[p]))/i for p in profs if p.graduation_year and
             (2018 - int(p.graduation_year) == i if i < 11 else 2018 - int(p.graduation_year) >= i)]
            for i in range(1, 12)]


def load_papers(prof) -> List[Tuple[str, str]]:
    """Uses the best source available: Scholar profile, then faculty directory, then Scholar search results.
    :return: a list of 2-tuples containing the journal title (and ideally only that) and a citation string. """

    # Try google scholar profile results first
    candidates = citations(load_scholar_papers(prof, ignore_search_results=True))
    # if there is no Scholar profile, try to use the faculty directory
    if len(candidates) == 0 and prof.paper_list_url:
        candidates = [(citation, citation) for citation in load_paper_list('paper_list', prof)
                      if get_year(citation) and get_year(citation) >= starting_year]
    # if we still have no results, then use Scholar search results
    if len(candidates) == 0:
        candidates = citations(load_scholar_papers(prof, ignore_search_results=False))
    # filter out non-articles
    taboo = ["editor", "call for papers", "annual report", "working paper"]
    real_candidates = []
    for c in candidates:
        is_taboo = False
        for t in taboo:
            if t in c[1].lower():
                is_taboo = True
        if not is_taboo:
            real_candidates.append(c)
    return real_candidates


def papers_in_top_journals(professors: List[Professor]) -> Dict[Professor, AnyStr]:
    """:return dict mapping from professor to a list of titles."""
    top_papers = {}
    # also count the total number of papers since start_date
    total_papers = 0
    for p in professors:
        candidates = load_papers(p)
        total_papers += len(candidates)
        # filter out papers in the top journals
        top_papers[p] = [citation for (journal, citation) in candidates if is_a_top_journal(journal)]
        # detect anomalies
        if len(top_papers[p]) > 30:
            print("\nWARNING: found %d top papers for %s" % (len(top_papers[p]), p.slug()))
            for paper in top_papers[p]:
                print("\t" + strip_whitespace(paper))
    print("\nTotal of %d papers since %s\n" % (total_papers, starting_year))
    return top_papers


def top_journal_pubs_for(school, professors: List[Professor]):
    candidates = []
    for p in professors:
        if p.affiliation == school:
            candidates.extend(load_papers(p))
    candidates = deduplicate(candidates,
                             lambda c: c[1],
                             lambda c1, c2: strings_are_similar(c1[1], c2[1]))
    return len([citation for (journal, citation) in candidates if is_a_top_journal(journal)])


def top_journal_pubs_for_profs_at_school(top_papers_for_each_prof: Dict[Professor, List[AnyStr]]) -> Dict[AnyStr, int]:
    """ :return: a dict mapping each school to a list of publication counts, one for each prof at that school."""
    return {school: [len(papers) for prof, papers in top_papers_for_each_prof.items() if prof.affiliation == school]
            for school in AFFILIATIONS}


def print_top_journal_results(top_papers_for_each_prof: Dict[Professor, List[AnyStr]]):
    for prof, papers in top_papers_for_each_prof.items():
        print(prof.slug())
        for paper in papers:
            print('\t' + paper)


def pubs_for_school_in_journal(professors, journal_name):
    return {school: sum([sum([is_in_journal(paper[0], journal_name) for paper in load_papers(prof)])
                         for prof in professors if prof.affiliation == school])
            for school in AFFILIATIONS}


def norm_str(my_string):
    return strip_whitespace(my_string.lower().translate(non_letter_remover))


def strings_are_similar(string1, string2):
    difference_allowed = 0.1  # allow a 10% difference in characters
    return editdistance.eval(norm_str(string1), norm_str(string2)) / (1.0*len(string1)) < difference_allowed


def papers_are_same(paper1, paper2):
    # below, sort author list to allow for reordering the names
    return strings_are_similar(paper1.title, paper2.title) \
           and strings_are_similar(''.join(sorted(paper1.authors)), ''.join(sorted(paper2.authors)))


def deduplicate(paper_list,
                sort_key=lambda paper: norm_str(paper.title),
                equality_tester=lambda p1, p2: papers_are_same(p1, p2)) -> List:
    paper_list = sorted(paper_list, key=sort_key)
    unique_papers = []
    for paper in paper_list:
        # check back a few places for matching titles in the sorted list
        for i in range(1,5):
            if len(unique_papers) >= i and equality_tester(paper, unique_papers[-i]):
                break
        else:
            unique_papers.append(paper)  # executed if the loop ended normally (no break)
    return unique_papers


def h_index_for_profs(professors: List[Professor]):
    """return an h-index (integer) based on all the publications of the professors passed-in,
    just for papers in the past ten years."""

    # gather and deduplicate publications, so that we don't count a paper twice if it had two authors at the school
    pubs = []
    for p in professors:
        pubs.extend(load_scholar_papers(p))
    pubs = deduplicate(pubs)

    return h_index_from_citations([c.scholar_citations for c in pubs])


def citations_for_profs_in_school(professors: List[Professor]):
    school_citations = {}
    for school in AFFILIATIONS:
        school_citations[school] = [count_citations(p) for p in professors if p.affiliation == school]
    return school_citations


def h_index_by_school(professors: List[Professor]):
    school_h_index= {}
    for school in AFFILIATIONS:
        school_h_index[school] = h_index_for_profs([p for p in professors if p.affiliation == school])
    return school_h_index


def h_index_from_citations(citation_counts):
    citation_counts = sorted(citation_counts)
    citation_counts.reverse()
    for i, c in enumerate(citation_counts):
        if int(c) < i+1:
            return i
    return len(citation_counts)


def sort_and_print_dict(dict):
    lst = sorted(dict.items(), key=lambda e: e[1] + (1E-10 if e[0] == 'Northwestern' else 0))  # Kellogg 1st on ties
    lst.reverse()
    for (key, v) in lst:
        # pad out schools names to 11 chars
        for i in range(0, 12 - len(key)):
            key += ' '
        val = ('%.2f' % v) if isinstance(v, float) else v
        print('  ', key, val)
    return lst


def normalize(school_dict, professors):
    normalized = {}
    for school, val in school_dict.items():
        profs_per_school = len([p for p in professors if p.affiliation == school])
        normalized[school] = val*1.0/profs_per_school
    return normalized


def normalize_to_age(top_papers_for_each_prof: Dict[Professor, List[AnyStr]]) -> Dict[Professor, float]:
    return {prof: len(top_papers_for_each_prof[prof])/(2018 - int(prof.graduation_year))
            for prof in [p for p in top_papers_for_each_prof if p.graduation_year]}


def approximate_missing_graduation_years(profs):
    """For profs with out a graduation_year defined, use the year of their earliest publication as an approximation.
    The Professor objects passed in are modified with the new graduation_year."""
    for prof in profs:
        if not prof.graduation_year:
            # Note that we use the full list of papers, including those older than ten years.
            paper_years = []
            for folder in ['scholar_profile', 'scholar_search', 'paper_list']:
                paper_years.extend([get_year(paper) for paper in load_paper_list(folder, prof)])
            paper_years = [p for p in paper_years if p]  # eliminate None values
            if len(paper_years) > 0:
                prof.graduation_year = min(paper_years)


def plot(pdf_pages, title, dict):
    print('\n%s:' % title)
    data = sort_and_print_dict(dict)
    # purple bar for kellogg
    plt.bar(range(0,len(data)),
            [e[1] if 'Northwestern' in e[0] else 0 for e in data], color=[.29,0,.51])
    # gray bar for other schools
    plt.bar(range(0,len(data)),
            [0 if 'Northwestern' in e[0] else e[1] for e in data], color=[0.8,0.8,0.8])
    plt.xticks(range(len(data)),
               tuple(['Kellogg' if e[0] == 'Northwestern' else e[0] for e in data]),
               rotation=30)
    plt.gca().yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))  # only use integer y ticks
    plt.gca().set_axisbelow(True)
    plt.gca().yaxis.grid(True, linewidth=0.25)
    plt.title(title)
    plt.gcf().tight_layout()
    plt.savefig(pdf_pages, format='pdf')
    plt.close()


def boxplot(pdf_pages, title, dict, logscale=False):
    # sort schools by their median value
    data = sorted(dict.items(), key=lambda entry: statistics.median(entry[1])
                  + (1E-10 if entry[0] == 'Northwestern' else 0))  # show Kellogg first if tied
    data.reverse()

    if not logscale:
        plt.figure(figsize=(4,7))

    box = plt.boxplot([e[1] for e in data], notch=False, patch_artist=True,
                      medianprops={'color': 'black', 'linewidth': 2.5},
                      boxprops={'linewidth': 0}, whis='range')

    for i, patch in enumerate(box['boxes']):
        if data[i][0] == 'Northwestern':
            patch.set_facecolor([.29, 0, .51])
        else:
            patch.set_facecolor([0.8, 0.8, 0.8])
    plt.xticks(range(1, len(data)+1),
               tuple(['Kellogg' if e[0] == 'Northwestern' else e[0] for e in data]),
               rotation=30)
    if max(max([e[1] for e in data])) > 2:
        plt.gca().yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))  # only use integer y ticks
    plt.gca().set_axisbelow(True)
    if logscale:
        plt.gca().set_yscale('log')
    else:
        # start y axis at zero
        plt.ylim([0, plt.ylim()[1]])
    plt.gca().yaxis.grid(True, linestyle=':', linewidth=0.25)
    plt.title(title)
    plt.gcf().tight_layout()
    plt.savefig(pdf_pages, format='pdf')
    plt.close()


def broken_boxplot(pdf_pages, title, dict, breakpoint):
    # sort schools by their median value
    data = sorted(dict.items(), key=lambda entry: statistics.median(entry[1])
                  + (1E-10 if entry[0] == 'Northwestern' else 0))  # show Kellogg first if tied
    data.reverse()

    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharex=True, figsize=(4, 6))
    # plot same data on both subplots
    for ax in [ax_top, ax_bottom]:
        box = ax.boxplot([e[1] for e in data], notch=False, patch_artist=True,
                         medianprops={'color': 'black', 'linewidth': 2.5},
                         boxprops={'linewidth': 0}, whis='range')
        for i, patch in enumerate(box['boxes']):
            if data[i][0] == 'Northwestern':
                patch.set_facecolor([.29, 0, .51])
            else:
                patch.set_facecolor([0.8, 0.8, 0.8])
        #ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))  # only use integer y ticks
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, linestyle=':', linewidth=0.25)
    plt.sca(ax_bottom)
    plt.xticks(range(1, len(data)+1),
               tuple(['Kellogg' if e[0] == 'Northwestern' else e[0] for e in data]),
               rotation=30)
    # define axis break
    ax_top.set_ylim(breakpoint + 10E-3,  # add a little so that we don't repeat the ytick label
                    ax_top.get_ylim()[1])
    ax_bottom.set_ylim(0, breakpoint)
    ## hide the spines between ax and ax2
    #ax_top.spines['bottom'].set_visible(False)
    #ax_bottom.spines['top'].set_visible(False)

    ax_top.set_title(title)
    plt.gcf().tight_layout()
    plt.savefig(pdf_pages, format='pdf')
    plt.close()


def plot_citation_aging(aging):
    prof_count = [len(cites) for cites in aging]
    print('\n%f%% of faculty have >= 10 years since graduation\n' % (100 * prof_count[-1] / sum(prof_count)))

    plt.bar([age for age, count in enumerate(prof_count)],
            [count for age, count in enumerate(prof_count)],
            label="sample size", color=[0.8,0.8,0.8])
    plt.xticks([age for age, cites in enumerate(prof_count)],
               [age if age < 10 else '>=10' for age, cites in enumerate(prof_count)])
    plt.xlabel("Years since professor's graduate degree")
    plt.ylabel("Number of faculty")
    plt.gca().set_axisbelow(True)
    plt.gca().yaxis.grid(True, linewidth=0.25)
    plt.gcf().tight_layout()
    plt.savefig("age_dist.pdf")
    plt.close()

    aging_boxplot(aging, "Citations per professor", "citation_aging.pdf")


def aging_boxplot(aging, title, filename):
    box = plt.boxplot([cites for age, cites in enumerate(aging)], notch=False, patch_artist=True,
                      medianprops={'color': 'black', 'linewidth': 2.5},
                      boxprops={'linewidth': 0}, whis='range')
    for i, patch in enumerate(box['boxes']):
        patch.set_facecolor([0.8, 0.8, 0.8])
    plt.gca().set_axisbelow(True)
    plt.gca().set_yscale('log')
    plt.gca().yaxis.grid(True, linestyle=':', linewidth=0.25)
    plt.xticks([age+1 for age, cites in enumerate(aging)],
               [age if age < 10 else '>=10' for age, cites in enumerate(aging)])
    plt.xlabel("Years since professor's graduate degree")
    plt.title(title)
    plt.gcf().tight_layout()
    plt.savefig(filename)
    plt.close()


def plot_early_dist(early_profs):
    plt.figure(figsize=(4, 8))
    for i, school in enumerate(AFFILIATIONS):
        plt.subplot(len(AFFILIATIONS), 1, i + 1)
        plt.title('Kellogg' if school == 'Northwestern' else school)
        aging = citation_aging_report([p for p in early_profs if p.affiliation == school])
        prof_count = [len(cites) for cites in aging ]
        plt.bar([age for age, count in enumerate(prof_count)],
                [count for age, count in enumerate(prof_count)],
                color=[.29,0,.51] if school == 'Northwestern' else [0.8,0.8,0.8])
        plt.tick_params(
            axis='x',  # changes apply to the x-axis
            which='both',  # both major and minor ticks are affected
            bottom='off' if i < len(AFFILIATIONS) - 1 else 'on',
            top='off',  # ticks along the top edge are off
            labelbottom='off')  # labels along the bottom edge are off
        plt.xticks([age for age, cites in enumerate(prof_count)],
                   [age for age, cites in enumerate(prof_count)])
    plt.xlabel("Years since professor's graduate degree")
    plt.gca().set_axisbelow(True)
    plt.gca().yaxis.grid(True, linewidth=0.25)
    plt.gcf().tight_layout()
    plt.savefig("early_dist.pdf")
    plt.close()


def plot_early_frac(profs, early_profs):
    early = {school: len([p for p in early_profs if p.affiliation == school]) for school in AFFILIATIONS}
    pp = PdfPages('early_frac.pdf')
    plot(pp, 'Fraction of faculty who are early-career', normalize(early, profs))
    pp.close();


def print_professors(profs):
    for school in AFFILIATIONS:
        print()
        print('\\textbf{%s}:' % school)
        for p in sorted(profs, key=lambda prof: prof.first_last_name()[1]):
            if p.affiliation == school:
                print('%s.~%s,%s' % (p.first_last_name()[0][0], p.first_last_name()[1],
                                     '*' if p.graduation_year and int(p.graduation_year) >= 2007 else ''))


def kellogg_dept_labelled_profs(profs) -> List[Professor]:
    """Return copies of the kellogg profs, with the "school" field now referring to their dept within Kellogg."""
    dept_profs = []
    for p in profs:
        if p.school=="Northwestern":
            copy = p.copy()
            for dept, prof_list in KELLOGG_DEPTS.items():
                for dept_p in prof_list:
                    if dept_p == p.slug():
                        copy.affiliation = dept
                        break
            dept_profs.append(copy)
    return dept_profs


def all_analyses():
    gs = GoogleSheets()
    profs = gs.read_profs()
    for p in profs:
        p.affiliation = p.school  # later we will do an analysis by department
    # remove hidden profs
    profs = [p for p in profs if not p.hidden]
    approximate_missing_graduation_years(profs)
    print_professors(profs)

    # global paper_folders
    # # just consider profs with a google scholar profile
    # paper_folders = ['scholar_profile']
    # profs = [p for p in profs if p.google_scholar_url]
    # print('Only considering the %d professors with Google Scholar profiles.' % len(profs))

    print('Looking exclusively at papers published in %s and later.' % starting_year)
    plot_citation_aging(citation_aging_report(profs))
    aging_boxplot(prestigious_rate_aging_report(profs), "Career-average prestigious publications per year",
                  "prestigious_rate_aging.pdf")

    run_analyses(profs, "plots_all.pdf")
    # just consider profs who finished their PhD within the past ten years
    early_profs = [p for p in profs if p.graduation_year and p.graduation_year >= starting_year]
    plot_early_dist(early_profs)
    plot_early_frac(profs, early_profs)
    run_analyses(early_profs, "plots_early.pdf")

    # do an inter-departmental comparison of Kellogg depts
    global AFFILIATIONS
    AFFILIATIONS = KELLOGG_DEPTS.keys()  # this is a hack to plot dept results like school results
    run_analyses(kellogg_dept_labelled_profs(profs), "plots_kellogg_dept.pdf")


def run_analyses(profs, pdf_output_filename):
    pp = PdfPages(pdf_output_filename)

    plot(pp, 'Faculty count', {school:len([p for p in profs if p.affiliation==school]) for school in AFFILIATIONS})

    citations = citations_for_profs_in_school(profs)
    citations_per_school = {school: sum(cites) for school, cites in citations.items()}
    plot(pp, 'Citations', citations_per_school)
    boxplot(pp, 'Citations per professor', citations, logscale=True)
    plot(pp, 'Mean citations per professor', normalize(citations_per_school, profs))
    plot(pp, 'Median citations per professors', {school: statistics.median(cites) for school, cites in citations.items()})

    plot(pp, 'School h-index', h_index_by_school(profs))

    j_stats = {school: top_journal_pubs_for(school, profs) for school in AFFILIATIONS}
    plot(pp, 'Prestigious article count', j_stats)
    top_papers = papers_in_top_journals(profs)
    top_pubs_per_prof = top_journal_pubs_for_profs_at_school(top_papers)
    boxplot(pp, 'Prestigious articles per professor', top_pubs_per_prof)
    plot(pp, 'Mean prestigious articles per professor',
         {school: statistics.mean(cites) for school, cites in top_pubs_per_prof.items()})
    plot(pp, 'Median prestigious articles per professor',
         {school: statistics.median(cites) for school, cites in top_pubs_per_prof.items()})
    prof_ppub_rate = normalize_to_age(top_papers);
    school_ppub_rate = {school: [rate for prof, rate in prof_ppub_rate.items() if prof.affiliation == school]
                        for school in AFFILIATIONS}
    boxplot(pp, 'Prestigious articles per professor, per year', school_ppub_rate)
    plot(pp, 'Mean faculty prestigious publication rate',
         {school: statistics.mean(school_ppub_rate[school]) for school in AFFILIATIONS})
    plot(pp, 'Median faculty prestigious publication rate',
         {school: statistics.median(school_ppub_rate[school]) for school in AFFILIATIONS})
    for j in TOP_JOURNALS:
        title = j.title().replace(' Of ', ' of ').replace(' And ', ' and ').replace(' The ', ' the ')\
            .replace('Rand J', 'RAND J')
        plot(pp, title, pubs_for_school_in_journal(top_papers, j))
    pp.close()

    pp = PdfPages(pdf_output_filename.replace('.pdf', '_tall.pdf'))
    broken_boxplot(pp, 'Prestigious articles per professor', top_pubs_per_prof, 8)
    broken_boxplot(pp, 'Prestigious articles per professor, per year', school_ppub_rate, 0.8)
    pp.close()


class Test(unittest.TestCase):
    def test_top_journals(self):
        self.assertTrue(is_a_top_journal("Econometrica"))
        self.assertTrue(is_a_top_journal("Econometrica. "))
        self.assertTrue(is_a_top_journal("Proc. Natl. Academy of Sciences"))
        self.assertTrue(is_a_top_journal("Manufacturing and Service Operations Management"))
        self.assertFalse(is_a_top_journal('American Journal of Nature'))

    def test_h_index(self):
        self.assertEqual(2, h_index_from_citations([5, 2, 1]))
        self.assertEqual(2, h_index_from_citations([3, 3, 1]))
        self.assertEqual(1, h_index_from_citations([9]))
        self.assertEqual(0, h_index_from_citations([]))
        self.assertEqual(0, h_index_from_citations([0, 0]))
        self.assertEqual(1, h_index_from_citations([1, 1, 1]))

    def test_deduplicate_papers(self):
        self.assertEqual(1, len(deduplicate([
            Paper(title='Why and How to Design a Contingent Convertible Debt Requirement',
                  authors='RJ Herring, CW Calomiris', venue='', year='', scholar_citations=''),
            Paper(title='Why and how to design a contingent convertible debt requirement',
                  authors='CW Calomiris, RJ Herring', venue='', year='', scholar_citations='')
        ])))
        self.assertEqual(2, len(deduplicate([
            Paper(title='Why and How to Design a Contingent Convertible Debt Requirement.',
                  authors='RJ Herring, CW Calomiris', venue='', year='', scholar_citations=''),
            Paper(title='Why and how to design a contingent convertible debt requirement',
                  authors='CW Calomiris, RJ Herring', venue='', year='', scholar_citations=''),
            Paper(title='Why and how to design a contingent convertible debt',
                  authors='CW Calomiris, RJ Herring', venue='', year='', scholar_citations='')
        ])))

    def test_abbreviate(self):
        self.assertEqual('manufacturing service operations mgmt',
                         abbreviate('Manufacturing and Service Operations Management'))
        self.assertTrue(is_in_journal(
            'Bob Smith. "My great paper." Manufacturing & Service Operations Management. (2017).',
            'manufacturing and service operations management'
        ))

if __name__ == '__main__':
    # unittest.main()
    all_analyses()
