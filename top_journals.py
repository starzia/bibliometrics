import unittest
import string
from professor import Professor
from typing import List
from professor_scraper import load_paper_list
from google_scholar import Paper, STARTING_YEAR


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
        # try google scholar profile first
        if p.google_scholar_url:
            for paper in load_papers('scholar_profile', p):
                candidates[paper.venue] = paper.pretty_citation()
        # next try google scholar search results
        else:
            for paper in load_papers('scholar_search', p):
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
    for school, count in school_count.items():
        print('%s:\t%f' % (school, count*1.0/profs_per_school[school]))


def print_results(professors):
    top_papers = count_papers_in_top_journals(professors)

    for p, papers in top_papers.items():
        print(p.slug())
        for paper in papers:
            print('\t' + paper)


class TestTopJournals(unittest.TestCase):
    def test(self):
        self.assertTrue(is_a_top_journal("Econometrica"))
        self.assertTrue(is_a_top_journal("Econometrica. "))
        self.assertTrue(is_a_top_journal("Proc. Natl. Academy of Sciences"))
        self.assertFalse(is_a_top_journal('American Journal of Nature'))

if __name__ == '__main__':
    unittest.main()