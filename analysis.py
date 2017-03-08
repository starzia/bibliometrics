import pprint
import operator
import unittest
import statistics
import string
from professor import Professor
from typing import List
from professor_scraper import load_paper_list
from google_scholar import Paper, STARTING_YEAR
from google_sheets import GoogleSheets

SCHOOLS = ['Northwestern', 'Harvard', 'Chicago', 'MIT', 'Stanford', 'UPenn', 'Berkeley', 'Yale', 'Columbia']

ABBREVIATIONS = {
    'the': None,
    'of': None,
    'journal': 'j',
    'review': 'rev',
    'research': 'res',
    'and': '&',
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
    'manufacturing and service operations',

    'psychological science',
    'journal of personality and social psychology',
    'organizational behavior and human decision processes',

    'american sociological review',
    'american journal of sociology',
    'sociological science',

    'administrative science quarterly',
    'organizational science',
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
punctuation_remover = str.maketrans('', '', string.punctuation)


def abbreviate(journal_name):
    output = []
    for tok in journal_name.lower().translate(punctuation_remover).split(' '):
        if tok in ABBREVIATIONS:
            if ABBREVIATIONS[tok]:
                output.append(ABBREVIATIONS[tok])
        else:
            output.append(tok)
    return ' '.join(output)


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
        return  abbreviate(journal) in abbreviated_name


# these variables control which papers are considered
paper_folders = ['scholar_profile', 'scholar_search']
starting_year = STARTING_YEAR


def load_papers(prof):
    global paper_folders, starting_year
    papers = []
    for f in paper_folders:
        papers.extend([p for p in [Paper.from_string(s) for s in load_paper_list(f, prof)] if p.year > starting_year])
    return papers


def count_citations(prof):
    return sum(int(paper.scholar_citations) for paper in load_papers(prof))


def load_papers_including_html(prof):
    candidates = []  # a list of 2-tuples containing the journal title (and ideally only that) and a citation string
    # Try google scholar results first
    for paper in load_papers(prof):
        candidates.append((paper.venue, paper.pretty_citation()))
    # if there were no google scholar search results, then use the faculty directory, if available
    if len(candidates) == 0 and prof.paper_list_url:
        candidates = [(citation, citation) for citation in load_paper_list('paper_list', prof)]
    return candidates


def count_papers_in_top_journals(professors: List[Professor]):
    # maps from professor to a list of titles
    top_papers = {}
    for p in professors:
        candidates = load_papers_including_html(p)
        # filter out papers in the top journals
        top_papers[p] = [citation for (journal, citation) in candidates if is_a_top_journal(journal)]
    return top_papers


def top_journal_pubs_for_school(professors: List[Professor]):
    top_papers = count_papers_in_top_journals(professors)
    return {school: [len(top_papers[p]) for p in professors if p.school == school] for school in SCHOOLS}


def print_top_journal_results(professors):
    top_papers = count_papers_in_top_journals(professors)

    for p, papers in top_papers.items():
        print(p.slug())
        for paper in papers:
            print('\t' + paper)


def pubs_for_school_in_journal(professors, journal_name):
    return {school: sum([sum([is_in_journal(paper[0], journal_name) for paper in load_papers_including_html(prof)])
                         for prof in professors if prof.school == school])
            for school in SCHOOLS}


def h_index_for_profs(professors: List[Professor]):
    """return an h-index (integer) based on all the publications of the professors passed-in,
    just for papers in the past ten years."""

    citation_counts = []
    for p in professors:
        for paper in load_papers(p):
            citation_counts.append(paper.scholar_citations)
    return h_index_from_citations(citation_counts)


def citations_for_profs_in_school(professors: List[Professor]):
    school_citations = {}
    for school in SCHOOLS:
        school_citations[school] = [count_citations(p) for p in professors if p.school == school]
    return school_citations


def school_fcn(school_dict, fcn):
    return {school: fcn(school_dict[school]) for school in SCHOOLS}


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


def print_sorted_dict(dict):
    lst = sorted(dict.items(), key=operator.itemgetter(1))
    lst.reverse()
    for (k, v) in lst:
        key = k
        if key == 'Northwestern':
            key = "__Kellogg__"
        # pad out schools names to 11 chars
        for i in range(0, 11 - len(key)):
            key += ' '
        val = ('%.2f' % v) if isinstance(v, float) else v
        print('  ', key, val)


def normalize(school_dict, professors):
    normalized = {}
    for school, val in school_dict.items():
        profs_per_school = len([p for p in professors if p.school == school])
        normalized[school] = val*1.0/profs_per_school
    return normalized


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

    print('\nCitations:')
    citations = citations_for_profs_in_school(profs)
    print_sorted_dict(school_fcn(citations, sum))
    print('Mean per prof:')
    print_sorted_dict(normalize(school_fcn(citations, sum), profs))
    print('Median per prof:')
    print_sorted_dict(school_fcn(citations, statistics.median))

    print('\nSchool h10-index:')
    print_sorted_dict(h_index_by_school(profs))

    print('\nPublications in top journals:')
    j_stats = top_journal_pubs_for_school(profs)
    print_sorted_dict(school_fcn(j_stats, sum))
    print('Mean per prof:')
    print_sorted_dict(normalize(school_fcn(j_stats, sum), profs))
    print('Median per prof:')
    print_sorted_dict(school_fcn(j_stats, statistics.median))

    print('\nPer-publication stats:')
    for j in TOP_JOURNALS:
        print(' '+j)
        print_sorted_dict(pubs_for_school_in_journal(profs, j))


class Test(unittest.TestCase):
    def test_top_journals(self):
        self.assertTrue(is_a_top_journal("Econometrica"))
        self.assertTrue(is_a_top_journal("Econometrica. "))
        self.assertTrue(is_a_top_journal("Proc. Natl. Academy of Sciences"))
        self.assertFalse(is_a_top_journal('American Journal of Nature'))

    def test_h_index(self):
        self.assertEqual(2, h_index_from_citations([5, 2, 1]))
        self.assertEqual(2, h_index_from_citations([3, 3, 1]))
        self.assertEqual(1, h_index_from_citations([9]))
        self.assertEqual(0, h_index_from_citations([]))
        self.assertEqual(0, h_index_from_citations([0, 0]))
        self.assertEqual(1, h_index_from_citations([1, 1, 1]))

if __name__ == '__main__':
    all_analyses()
