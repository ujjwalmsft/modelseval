import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import FunctionsIcon from '@mui/icons-material/Functions';
import TimelineIcon from '@mui/icons-material/Timeline';
import ScatterPlotIcon from '@mui/icons-material/ScatterPlot';
import StarIcon from '@mui/icons-material/Star';

export interface MetricInfo {
  name: string;
  shortName?: string;
  icon?: React.ReactNode;
  description: string;
  threshold?: string;
  useCases?: string[];
  moreInfoUrl?: string;
}

export const metricInfoData: Record<string, MetricInfo> = {
  BLEU: {
    name: 'BLEU Score',
    shortName: 'BLEU',
    icon: <AutoAwesomeIcon color="primary" />,
    description:
      'BLEU (Bilingual Evaluation Understudy) is a metric for evaluating a generated sentence to a reference sentence, commonly used for machine translation and text generation. It measures the overlap of n-grams between the generated and reference texts.',
    threshold: '0.25 or higher is generally considered decent for generation tasks.',
    useCases: [
      'Machine translation quality evaluation',
      'Text summarization',
      'Paraphrase generation',
    ],
    // moreInfoUrl: 'https://en.wikipedia.org/wiki/BLEU',
  },
  'ROUGE-1': {
    name: 'ROUGE-1 Score',
    shortName: 'ROUGE-1',
    icon: <FunctionsIcon color="secondary" />,
    description:
      'ROUGE-1 measures the overlap of unigrams (single words) between the generated and reference texts. It is widely used for evaluating summarization and generation tasks.',
    threshold: '0.4 or higher is often considered good for summarization.',
    useCases: [
      'Text summarization evaluation',
      'Document comparison',
      'Paraphrase detection',
    ],
    // moreInfoUrl: 'https://en.wikipedia.org/wiki/ROUGE_(metric)',
  },
  'ROUGE-L': {
    name: 'ROUGE-L Score',
    shortName: 'ROUGE-L',
    icon: <TimelineIcon color="action" />,
    description:
      'ROUGE-L measures the longest common subsequence between the generated and reference texts, capturing fluency and sequence similarity.',
    threshold: '0.3 or higher is typical for good summaries.',
    useCases: [
      'Text summarization evaluation',
      'Sequence similarity analysis',
    ],
    // moreInfoUrl: 'https://en.wikipedia.org/wiki/ROUGE_(metric)',
  },
  'Cosine Similarity': {
    name: 'Cosine Similarity',
    shortName: 'Cosine Sim.',
    icon: <ScatterPlotIcon color="success" />,
    description:
      'Cosine Similarity measures the cosine of the angle between two non-zero vectors, often used to assess semantic similarity between embeddings of generated and reference texts.',
    threshold: '0.85 or higher indicates strong semantic similarity.',
    useCases: [
      'Semantic similarity evaluation',
      'Embedding-based retrieval',
      'Plagiarism detection',
    ],
    // moreInfoUrl: 'https://en.wikipedia.org/wiki/Cosine_similarity',
  },
  'Semantic Cosine Similarity': {
    name: 'Semantic Cosine Similarity',
    shortName: 'Semantic Cosine Sim.',
    icon: <ScatterPlotIcon color="info" />,
    description:
      'Semantic Cosine Similarity is a variant of cosine similarity that uses semantic embeddings (such as from transformer models) to compare the meaning of generated and reference texts.',
    threshold: '0.90 or higher is considered very strong semantic alignment.',
    useCases: [
      'Semantic evaluation of generated text',
      'Assessing paraphrase quality',
      'Semantic search and retrieval',
    ],
    // moreInfoUrl: 'https://en.wikipedia.org/wiki/Cosine_similarity',
  },
  Combined: {
    name: 'Combined Score',
    shortName: 'Combined',
    icon: <StarIcon color="warning" />,
    description:
      'The Combined Score is an aggregate metric that blends several individual metrics (BLEU, ROUGE, Cosine Similarity, etc.) to provide a holistic evaluation of the generated text quality.',
    threshold: 'Depends on the aggregation method; higher is better.',
    useCases: [
      'Overall model performance ranking',
      'Leaderboard scoring',
      'General-purpose text evaluation',
    ],
    // moreInfoUrl: '',
  },
};