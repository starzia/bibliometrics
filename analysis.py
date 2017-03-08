import pprint
import operator
import unittest
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
    'journal of economic theory'
    'review of economic studies',
    'rand journal of economics',
    'american economic review: micro',
    'american economic journal: macroeconomics',
    'journal of monetary economics',

    'journal of finance',
    'review of financial studies',
    'journal of financial economics',

    'journal of consumer research',
    'journal of market research',
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
    abbreviated_name = abbreviate(contains_journal_name)
    for j in TOP_JOURNALS:
        if abbreviate(j) in abbreviated_name:
            return True
    for j in HIGH_COLLISION_TOP_JOURNALS:
        if abbreviate(j) == abbreviated_name:
            return True
    return False


def load_papers(folder_name, prof):
    return [p for p in [Paper.from_string(s) for s in load_paper_list(folder_name, prof)] if p.year > STARTING_YEAR]


def count_papers_in_top_journals(professors: List[Professor]):
    # maps from professor to a list of titles
    top_papers = {}
    for p in professors:
        candidates = {}  # maps from string containing the journal title (and ideally only that) to a citation string
        # Try google scholar results first.  A given person will have one type of results or the other, but not both.
        for paper in load_papers('scholar_profile', p) + load_papers('scholar_search', p):
            candidates[paper.venue] = paper.pretty_citation()
        # if there were no google scholar search results, then use the faculty directory, if available
        if len(candidates) == 0 and p.paper_list_url:
            for citation in load_paper_list('paper_list', p):
                candidates[citation]: citation

        # filter out papers in the top journals
        top_papers[p] = [citation for journal, citation in candidates.items() if is_a_top_journal(journal)]
    return top_papers


def print_top_journal_stats(professors: List[Professor]):
    top_papers = count_papers_in_top_journals(professors)

    school_count = {}
    profs_per_school = {}
    for p, papers in top_papers.items():
        if p.school not in school_count:
            school_count[p.school] = 0
            profs_per_school[p.school] = 0
        school_count[p.school] += len(papers)
        profs_per_school[p.school] += 1
    print("Total:")
    print_sorted_dict(school_count)

    normalized = {}
    for school, count in school_count.items():
        normalized[school] = count*1.0/profs_per_school[school]
    print("Per professor:")
    print_sorted_dict(normalized)


def print_top_journal_results(professors):
    top_papers = count_papers_in_top_journals(professors)

    for p, papers in top_papers.items():
        print(p.slug())
        for paper in papers:
            print('\t' + paper)


def h_index_for_profs(professors: List[Professor]):
    """return an h-index (integer) based on all the publications of the professors passed-in,
    just for papers in the past ten years."""

    citation_counts = []
    for p in professors:
        # use google scholar profiles and google scholar search results
        for paper in load_papers('scholar_profile', p) + load_papers('scholar_search', p):
            citation_counts.append(paper.scholar_citations)
    return h_index_from_citations(citation_counts)


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
    for (k, v) in sorted(dict.items(), key=operator.itemgetter(1)):
        print('  ', k, '\t', v)


def all_analyses():
    gs = GoogleSheets()
    profs = gs.read_profs()
    # remove hidden profs
    profs = [p for p in profs if not p.hidden]

    print('\nSchool h10-index:')
    print_sorted_dict(h_index_by_school(profs))

    print('\nPublications in top journals:')
    print_top_journal_stats(profs)



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
