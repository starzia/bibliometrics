import pprint
import operator
import unittest
import statistics
import string

import editdistance
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker

from professor import Professor
from typing import List, Dict, AnyStr
from professor_scraper import load_paper_list
from google_scholar import Paper, STARTING_YEAR, get_year
from google_sheets import GoogleSheets
from web_util import strip_whitespace

SCHOOLS = ['Northwestern', 'Harvard', 'Chicago', 'MIT', 'Stanford', 'UPenn', 'Berkeley', 'Yale', 'Columbia']

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


# these variables control which papers are considered
paper_folders = ['scholar_profile', 'scholar_search']
starting_year = STARTING_YEAR
ignored_scholar_citation_ids = set([])
try:
    with open('papers_to_ignore.txt', 'r') as f:
        ignored_scholar_citation_ids = set([l.replace('\n', '') for l in f.readlines()])
except FileNotFoundError:
    print("WARNING: did not find papers_to_ignore.txt")
paper_cache = {}


def load_papers(prof):
    global paper_folders, starting_year, paper_cache
    if prof not in paper_cache:
        papers = []
        for f in paper_folders:
            papers.extend([p for p in [Paper.from_string(s) for s in load_paper_list(f, prof)]
                           if p.year > starting_year and p.id not in ignored_scholar_citation_ids])
        paper_cache[prof] = papers
    return paper_cache[prof]


def count_citations(prof):
    return sum(int(paper.scholar_citations) for paper in load_papers(prof))


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


def load_papers_including_html(prof):
    candidates = []  # a list of 2-tuples containing the journal title (and ideally only that) and a citation string
    # Try google scholar results first
    for paper in load_papers(prof):
        candidates.append((paper.venue, paper.pretty_citation()))
    # if there were no google scholar search results, then use the faculty directory, if available
    if len(candidates) == 0 and prof.paper_list_url:
        candidates = [(citation, citation) for citation in load_paper_list('paper_list', prof)
                      if get_year(citation) and get_year(citation) >= starting_year]
    return candidates


def papers_in_top_journals(professors: List[Professor]) -> Dict[Professor, AnyStr]:
    """:return dict mapping from professor to a list of titles"""
    top_papers = {}
    for p in professors:
        candidates = load_papers_including_html(p)
        # filter out papers in the top journals
        top_papers[p] = [citation for (journal, citation) in candidates if is_a_top_journal(journal)]
    return top_papers


def top_journal_pubs_for(school, professors: List[Professor]):
    candidates = []
    for p in professors:
        if p.school == school:
            candidates.extend(load_papers_including_html(p))
    candidates = deduplicate(candidates,
                             lambda c: c[1],
                             lambda c1, c2: strings_are_similar(c1[1], c2[1]))
    return len([citation for (journal, citation) in candidates if is_a_top_journal(journal)])


def top_journal_pubs_for_profs_at_school(top_papers_for_each_prof: Dict[Professor, List[AnyStr]]) -> Dict[AnyStr, int]:
    """ :return: a dict mapping each school to a list of publication counts, one for each prof at that school."""
    return {school: [len(papers) for prof, papers in top_papers_for_each_prof.items() if prof.school == school]
            for school in SCHOOLS}


def print_top_journal_results(top_papers_for_each_prof: Dict[Professor, List[AnyStr]]):
    for prof, papers in top_papers_for_each_prof.items():
        print(prof.slug())
        for paper in papers:
            print('\t' + paper)


def pubs_for_school_in_journal(professors, journal_name):
    return {school: sum([sum([is_in_journal(paper[0], journal_name) for paper in load_papers_including_html(prof)])
                         for prof in professors if prof.school == school])
            for school in SCHOOLS}


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
        pubs.extend(load_papers(p))
    pubs = deduplicate(pubs)

    return h_index_from_citations([c.scholar_citations for c in pubs])


def citations_for_profs_in_school(professors: List[Professor]):
    school_citations = {}
    for school in SCHOOLS:
        school_citations[school] = [count_citations(p) for p in professors if p.school == school]
    return school_citations


def h_index_by_school(professors: List[Professor]):
    school_h_index= {}
    for school in SCHOOLS:
        school_h_index[school] = h_index_for_profs([p for p in professors if p.school == school])
    return school_h_index


def h_index_from_citations(citation_counts):
    citation_counts = sorted(citation_counts)
    citation_counts.reverse()
    for i, c in enumerate(citation_counts):
        if int(c) < i+1:
            return i
    return len(citation_counts)


def sort_and_print_dict(dict):
    lst = sorted(dict.items(), key=operator.itemgetter(1))
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
        profs_per_school = len([p for p in professors if p.school == school])
        normalized[school] = val*1.0/profs_per_school
    return normalized


def normalize_to_age(top_papers_for_each_prof: Dict[Professor, List[AnyStr]]) -> Dict[Professor, float]:
    return {prof: len(top_papers_for_each_prof[prof])/(2018 - int(prof.graduation_year))
            for prof in [p for p in top_papers_for_each_prof if p.graduation_year]}


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
    plt.gca().yaxis.grid(True)
    plt.title(title)
    plt.savefig(pdf_pages, format='pdf')
    plt.close()


def plot_citation_aging(aging):
    plt.bar([age for age, cites in enumerate(aging)],
            [len(cites) for age, cites in enumerate(aging)],
            label="sample size", color=[0.8,0.8,0.8])
    plt.xticks([age for age, cites in enumerate(aging)],
               [age if age < 10 else '>=10' for age, cites in enumerate(aging)])
    plt.xlabel("Years since faculty's graduation")
    plt.ylabel("Number of faculty")
    plt.gca().set_axisbelow(True)
    plt.gca().yaxis.grid(True)
    plt.savefig("age_dist.pdf")
    plt.close()

    plt.plot([age for age, cites in enumerate(aging)],
             [statistics.median(cites) for age, cites in enumerate(aging)],
             label="median citations")
    plt.plot([age for age, cites in enumerate(aging)],
             [statistics.mean(cites) for age, cites in enumerate(aging)], '--',
             label="mean citations")
    plt.xticks([age for age, cites in enumerate(aging)],
               [age if age < 10 else '>=10' for age, cites in enumerate(aging)])
    plt.xlabel("Years since faculty's graduation")
    plt.legend(loc=2)
    plt.ylim([0, 1500])
    plt.ylabel("Citations per faculty")
    plt.gca().set_axisbelow(True)
    plt.gca().yaxis.grid(True)
    plt.savefig("citation_aging.pdf")
    plt.close()


def plot_prestigious_rate_aging(aging):
    plt.plot([age for age, cites in enumerate(aging)],
             [statistics.median(cites) for age, cites in enumerate(aging)],
             label="median rate")
    plt.plot([age for age, cites in enumerate(aging)],
             [statistics.mean(cites) for age, cites in enumerate(aging)], '--',
             label="mean rate")
    plt.xticks([age for age, cites in enumerate(aging)],
               [age if age < 10 else '>=10' for age, cites in enumerate(aging)])
    plt.xlabel("Years since faculty's graduation")
    plt.legend(loc=1)
    plt.ylabel("Career-average prestigious publications per year")
    plt.ylim([0, 1.2])
    plt.gca().set_axisbelow(True)
    plt.gca().yaxis.grid(True)
    plt.savefig("presitigious_rate_aging.pdf")
    plt.close()


def all_analyses():
    gs = GoogleSheets()
    profs = gs.read_profs()
    # remove hidden profs
    profs = [p for p in profs if not p.hidden]

    global paper_folders, starting_year
    # # just consider profs with a google scholar profile
    # paper_folders = ['scholar_profile']
    # profs = [p for p in profs if p.google_scholar_url]
    # print('Only considering the %d professors with Google Scholar profiles.' % len(profs))

    print('Looking exclusively at papers published in %s and later.' % starting_year)
    plot_citation_aging(citation_aging_report(profs))
    plot_prestigious_rate_aging(prestigious_rate_aging_report(profs))

    run_analyses(profs, "plots_all.pdf")
    # just consider profs who finished their PhD within the past ten years
    run_analyses([p for p in profs if p.graduation_year and p.graduation_year >= starting_year], "plots_early.pdf")


def run_analyses(profs, pdf_output_filename):
    pp = PdfPages(pdf_output_filename)
    plot(pp, 'Faculty count', {school:len([p for p in profs if p.school==school]) for school in SCHOOLS})

    citations = citations_for_profs_in_school(profs)
    citations_per_school = {school: sum(cites) for school, cites in citations.items()}
    plot(pp, 'Citations', citations_per_school)
    plot(pp, 'Mean citations per faculty', normalize(citations_per_school, profs))
    plot(pp, 'Median citations per faculty', {school: statistics.median(cites) for school, cites in citations.items()})

    plot(pp, 'School h-index', h_index_by_school(profs))

    j_stats = {school: top_journal_pubs_for(school, profs) for school in SCHOOLS}
    plot(pp, 'Prestigious publication count', j_stats)
    plot(pp, 'Mean prestigious publications per faculty', normalize(j_stats, profs))
    top_papers = papers_in_top_journals(profs)
    plot(pp, 'Median prestigious publications per faculty',
         {school: statistics.median(cites)
          for school, cites in top_journal_pubs_for_profs_at_school(top_papers).items()})
    prof_ppub_rate = normalize_to_age(top_papers);
    plot(pp, 'Mean faculty prestigious publication rate',
         {school: statistics.mean([rate for prof, rate in prof_ppub_rate.items() if prof.school == school])
          for school in SCHOOLS})
    plot(pp, 'Median faculty prestigious publication rate',
         {school: statistics.median([rate for prof, rate in prof_ppub_rate.items() if prof.school == school])
          for school in SCHOOLS})
    for j in TOP_JOURNALS:
        title = j.title().replace(' Of ', ' of ').replace(' And ', ' and ').replace(' The ', ' the ')
        plot(pp, title, pubs_for_school_in_journal(top_papers, j))
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
